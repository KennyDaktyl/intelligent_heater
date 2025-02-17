import RPi.GPIO as GPIO
import time

# Ustawienie numeru pinu
PIN = 17

# Konfiguracja GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

try:
    while True:
        print("🟢 Włączam pin 17")
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(5)
        print("🔴 Wyłączam pin 17")
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(5)
except KeyboardInterrupt:
    print("🛑 Przerwano działanie programu.")
finally:
    GPIO.cleanup()
    print("🧹 GPIO wyczyszczone.")
