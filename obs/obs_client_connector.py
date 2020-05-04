#!/usr/bin/env python3

from urllib.request import urlopen
import obspython as obs
from time import sleep

# #######  PUT IP HERE!!! #########
url = "/obs-rec-status-change"
# #######      IP         #########


def check_url():
    file = urlopen(url)

    u = None
    for line in file:
        u += line.decode("utf-8")
    return u


def obs_case():
    u = check_url()
    if u == 'start':
        start_recording()
        return True

    elif u == 'stop':
        stop_recording()
        return True

    elif u == 'waiting':
        return False

    else:
        return f'Error with the server'


def start_recording():
    if status() is True:
        obs.obs_frontend_recording_start()
        return True
    else:
        return False


def status():
    return obs.obs_frontend_recording_active()


def stop_recording():
    if status() is False:
        obs.obs_frontend_recording_stop()
        return True
    else:
        return False


while True:
    time.wait()
    waiting = obs_case()
    if waiting is False:
        break
    sleep(5)