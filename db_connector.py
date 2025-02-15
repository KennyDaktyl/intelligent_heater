import psycopg2
from config import DB_CONFIG

def get_latest_power_value_with_timestamp():
    """ Pobiera najnowszą wartość mocy oraz timestamp z bazy danych """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        SELECT current_power, timestamp 
        FROM power_monitoring 
        ORDER BY timestamp DESC 
        LIMIT 1;
        """

        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            power = result[0]
            timestamp = result[1]
            return power, timestamp
        return None
    except Exception as e:
        print(f"Błąd połączenia z bazą danych: {e}")
        return None
