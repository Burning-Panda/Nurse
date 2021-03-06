# Code fetched from "https://pimylifeup.com/raspberry-pi-rfid-rc522/"
# Custom modification:
#   Time function to stop this program after a certain amount of time has elapsed.
#   This is done to prevent and overloading the server (pi).

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

reading = SimpleMFRC522()


def read():
    id = None
    start_time = time.time()

    try:
        while True:
            elapsed_time = time.time() - start_time
            et = round(elapsed_time)
            if et > 240:
                id = False
                break
            id = reading.read()
            break
    finally:
        GPIO.cleanup()
        return id
