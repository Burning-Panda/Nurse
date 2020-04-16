import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

reading = SimpleMFRC522()


def read():
    # id, text = None
    id = None
    start_time = time.time()

    try:
        while True:
            elapsed_time = time.time() - start_time
            et = round(elapsed_time)
            if et > 240:
                id = False
                break
            # id, text = reader.read()
            id = reading.read()
            break
    finally:
        GPIO.cleanup()
        return id
