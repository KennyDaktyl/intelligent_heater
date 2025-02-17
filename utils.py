import os
import logging
import smtplib
import pytz
import time

from datetime import datetime
from config import LOG_DIR

from email.message import EmailMessage

current_log_date = None  
warsaw_tz = pytz.timezone("Europe/Warsaw")


class WarsawTimeFormatter(logging.Formatter):
    """Formatter, który wymusza czas w Europe/Warsaw bez milisekund."""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=warsaw_tz)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

def setup_logging():
    """Konfiguracja logowania - przełączanie logów tylko raz na dobę."""
    global current_log_date

    # 🔧 Ustawienie strefy czasowej systemu
    os.environ["TZ"] = "Europe/Warsaw"
    time.tzset()

    now = datetime.now(warsaw_tz)  # Pobierz czas w Warszawie
    log_date = now.strftime('%Y-%m-%d')

    if log_date == current_log_date:
        return  

    current_log_date = log_date
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"log_{log_date}.log")

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    # 📌 Użycie niestandardowego formatowania czasu (bez milisekund!)
    formatter = WarsawTimeFormatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    logging.info(f"Logowanie skonfigurowane na plik: {log_file}")


def send_email_with_logs(operation_times):
    """
    Wysyła logi z bieżącego dnia oraz zestawienie czasowe na podany e-mail.
    """
    email = os.getenv("EMAIL")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

    if not email or not email_password:
        logging.error("Brak konfiguracji e-mail w pliku .env")
        return

    try:
        with open(log_file, "r") as log_file:
            log_content = log_file.read()

        # Przygotowanie zestawienia czasowego
        operation_summary = "Zestawienie czasowe pracy grzałki:\n"
        for start, end in operation_times:
            operation_summary += f"Włączona od {start} do {end}\n"
        operation_summary += "\n\n"

        msg = EmailMessage()
        msg["Subject"] = f"Logi Grzejnika Ręcznikowca z dnia {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = email
        msg["To"] = email
        msg.set_content(operation_summary + log_content)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email, email_password)
            server.send_message(msg)
            logging.info("Logi i zestawienie czasowe wysłane na e-mail.")
    except Exception as e:
        logging.error(f"Błąd podczas wysyłania e-maila: {e}")
        

def get_current_time():
    """Funkcja zwraca aktualny czas w strefie czasowej Warszawy."""
    return datetime.now(warsaw_tz)
