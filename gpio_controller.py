from config import GPIO_PIN

# Sprawdzenie dostępności RPi.GPIO
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    from mock_gpio import GPIO  # Import symulowanego modułu GPIO


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, GPIO.HIGH)  # Domyślnie wyłączone w logice odwrotnej


def turn_on():
    GPIO.output(GPIO_PIN, GPIO.LOW)  # Odwrócona logika - LOW = WŁĄCZONE
    print("PIN WŁĄCZONY")


def turn_off():
    GPIO.output(GPIO_PIN, GPIO.HIGH)  # HIGH = WYŁĄCZONE
    print("PIN WYŁĄCZONY")


def cleanup_gpio():
    GPIO.cleanup()
