import time
import logging
from db_connector import get_latest_power_value_with_timestamp
from gpio_controller import setup_gpio, turn_on, turn_off, cleanup_gpio
from config import CHECK_INTERVAL, POWER_THRESHOLD, EXPIRATION_TIME_SECONDS
from utils import setup_logging, send_email_with_logs, get_current_time, warsaw_tz # noqa


def main():
    setup_gpio()

    device_state = False
    last_email_sent_date = None
    work_sessions = []

    try:
        while True:
            setup_logging()
            now = get_current_time()

            if now.hour >= 22 and (last_email_sent_date is None or last_email_sent_date < now.date()): # noqa
                logging.info("📩 Wysyłam logi i zestawienie czasu pracy urządzenia.") # noqa

                send_email_with_logs(work_sessions)

                last_email_sent_date = now.date()
                work_sessions.clear()

            result = get_latest_power_value_with_timestamp()

            if result:
                power, timestamp = result

                if timestamp.tzinfo is None:
                    timestamp = warsaw_tz.localize(timestamp)

                now = get_current_time()
                age_seconds = (now - timestamp).total_seconds()

                if power is None:
                    if device_state:
                        logging.error(
                            f"AWARIA: Brak wartości `current_power`. Ostatni wpis: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}. WYŁĄCZANIE urządzenia." # noqa
                        )
                        turn_off()
                        device_state = False

                        if work_sessions and work_sessions[-1][1] is None:
                            work_sessions[-1][1] = now

                    time.sleep(CHECK_INTERVAL)
                    continue

                if age_seconds > EXPIRATION_TIME_SECONDS:
                    if device_state:
                        logging.error(
                            f"AWARIA: Przestarzały wpis ({timestamp.strftime('%Y-%m-%d %H:%M:%S')}), {age_seconds:.0f} sekund temu. WYŁĄCZANIE urządzenia." # noqa
                        )
                        turn_off()
                        device_state = False

                        if work_sessions and work_sessions[-1][1] is None:
                            work_sessions[-1][1] = now

                    time.sleep(CHECK_INTERVAL)
                    continue

                logging.info(
                    f"Odczytana moc: {power} kW (timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})" # noqa
                )

                if power > POWER_THRESHOLD and not device_state:
                    logging.info("Moc przekracza próg - WŁĄCZANIE urządzenia.")
                    turn_on()
                    device_state = True
                    work_sessions.append([timestamp, None])

                elif power <= POWER_THRESHOLD and device_state:
                    logging.info(
                        "Moc spadła poniżej progu - WYŁĄCZANIE urządzenia."
                    )
                    turn_off()
                    device_state = False
                    if work_sessions and work_sessions[-1][1] is None:
                        work_sessions[-1][1] = timestamp

            else:
                if device_state:
                    logging.error(
                        "AWARIA: Nie udało się pobrać danych z bazy. WYŁĄCZANIE urządzenia." # noqa
                    )
                    turn_off()
                    device_state = False

                    if work_sessions and work_sessions[-1][1] is None:
                        work_sessions[-1][1] = now

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logging.info("🛑 Program zatrzymany przez użytkownika.")
    finally:
        cleanup_gpio()
        logging.info("🧹 GPIO wyczyszczone.")


if __name__ == "__main__":
    main()
