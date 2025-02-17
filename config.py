import os

# Konfiguracja bazy danych
DB_CONFIG = {
    "host": "91.236.86.24",
    "port": 5432,
    "dbname": "inverter_data",
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
}

LOG_DIR = "logs"

GPIO_PIN = 17  # Numer pinu GPIO do włączania urządzenia
CHECK_INTERVAL = 60  # Czas oczekiwania w sekundach (3 minuty)
POWER_THRESHOLD = 2.5  # Próg mocy w kW
