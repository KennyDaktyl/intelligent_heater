import os
import time
import logging
import pytz
from datetime import datetime
from db_connector import get_latest_power_value_with_timestamp
from gpio_controller import setup_gpio, turn_on, turn_off, cleanup_gpio
from config import CHECK_INTERVAL, POWER_THRESHOLD
from utils import setup_logging, send_email_with_logs, get_current_time, warsaw_tz

def main():
    setup_gpio()
    setup_logging()

    device_state = False  # False = wyłączone, True = włączone
    last_email_sent_date = None  # Przechowuje datę ostatniej wysyłki e-maila
    work_sessions = []  # Przechowuje sesje pracy urządzenia

    try:
        while True:
            setup_logging()  # Aktualizacja logowania jeśli zmienił się dzień
            
            now = get_current_time()  # Pobieramy aktualny czas (zawiera strefę czasową)

            # 📬 **Sprawdzenie, czy jest po 22:00 i czy e-mail został już wysłany dziś**
            if now.hour >= 22 and (last_email_sent_date is None or last_email_sent_date < now.date()):
                logging.info("📩 Wysyłam logi i zestawienie czasu pracy urządzenia.")

                summary = "\n".join([f"Włączona od {start.strftime('%H:%M')} do {end.strftime('%H:%M')}" for start, end in work_sessions])
                email_body = f"Zestawienie czasowe pracy grzałki:\n{summary}"
                send_email_with_logs(email_body)  # Można dodać obsługę czasu pracy
                last_email_sent_date = now.date()  # Zapisujemy datę wysłania e-maila
                work_sessions.clear()

            result = get_latest_power_value_with_timestamp()
                    
            if result:
                power, timestamp = result

                # ✅ KONWERSJA TIMESTAMPU (jeśli jest bez strefy czasowej)
                if timestamp.tzinfo is None:
                    timestamp = warsaw_tz.localize(timestamp)  # Poprawnie lokalizujemy czas

                now = get_current_time()  # Aktualizujemy czas po konwersji
                age_seconds = (now - timestamp).total_seconds()  # Teraz oba czasy są `aware`

                # Sprawdzanie przestarzałych danych
                if power is None:
                    if device_state:  # Jeśli urządzenie było włączone, loguj i wyłącz
                        logging.error(f"⚠️ AWARIA: Brak wartości `current_power`. Ostatni wpis: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}). WYŁĄCZANIE urządzenia.")
                        turn_off()
                        device_state = False
                        
                    time.sleep(CHECK_INTERVAL)
                    continue

                if age_seconds > 181:
                    if device_state:
                        logging.error(f"⚠️ AWARIA: Przestarzały wpis ({timestamp.strftime('%Y-%m-%d %H:%M:%S')}), {age_seconds:.0f} sekund temu). WYŁĄCZANIE urządzenia.")
                        turn_off()
                        device_state = False
                        work_sessions.append([timestamp, None]) 
                    time.sleep(CHECK_INTERVAL)
                    continue

                # Logowanie wartości mocy
                logging.info(f"🔍 Odczytana moc: {power} kW (timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}))")

                # Decyzja o zmianie stanu urządzenia
                if power > POWER_THRESHOLD and not device_state:
                    logging.info("⚡ Moc przekracza próg - WŁĄCZANIE urządzenia.")
                    turn_on()
                    device_state = True
                    work_sessions.append([timestamp, None])

                elif power <= POWER_THRESHOLD and device_state:
                    logging.info("🔻 Moc spadła poniżej progu - WYŁĄCZANIE urządzenia.")
                    turn_off()
                    device_state = False
                    if work_sessions and work_sessions[-1][1] is None:
                        work_sessions[-1][1] = timestamp

            else:
                if device_state:
                    logging.error("🚨 AWARIA: Nie udało się pobrać danych z bazy. WYŁĄCZANIE urządzenia.")
                    turn_off()
                    device_state = False

            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logging.info("🛑 Program zatrzymany przez użytkownika.")
    finally:
        cleanup_gpio()
        logging.info("🧹 GPIO wyczyszczone.")

if __name__ == "__main__":
    main()
