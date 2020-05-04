#!/usr/bin/env python
# title             : obs_server.py
# description       : OBS server is an OBS script that will create a server to await commands from a the Pi
#                   :
# author            : André T. Lønvik
# date              : 2020 05 04
# version           : 0.1
# usage             : python obs_server.py
# dependencies      : - Python 3.6 (https://www.python.org/)
#                   :
# notes             : Follow this step for this script to work:
#                   : Python:
#                   :   1. Install python (v3.6 and 64 bits, this is important)
#                   :   2. Install pywin32 (not with pip, but with installer)
#                   : OBS:
#                   :   1. Create a GDI+ Text Source with the name of your choice
#                   :   2. Go to Tools › Scripts
#                   :   3. Click the "+" button and add this script
#                   :   5. Set the same source name as the one you just created
#                   :   6. Check "Enable"
#                   :   7. Click the "Python Settings" rab
#                   :   8. Select your python install path
#                   :
# python_version    : 3.6+
# ==============================================================================

import time
import zmq
import obspython as obs

context = zmq.Context()
socket = context.socket(zmq.REP)

working = True
enabled = True
debug_mode = False
port = 5555
socket.bind("tcp://*:%d" % port)
room = 1
source_name = ''


def script_defaults(settings):
    global debug_mode
    if debug_mode:
        print("Calling defaults")

    global enabled
    global room

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_int(settings, "room", room)
    obs.obs_data_set_default_int(settings, "port", port)


def script_load(settings):
    global debug_mode
    if debug_mode:
        print("[CS] Loaded script.")


def script_properties():
    global debug_mode
    if debug_mode:
        print("[CS] Loaded properties.")

    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug_mode", "Debug Mode")
    obs.obs_properties_add_int(props, "room", "Room Number", 1, 2, 3, 4)
    return props


def script_save(settings):
    global debug_mode
    if debug_mode:
        print("[CS] Saved properties.")

    script_update(settings)


def script_unload():
    global debug_mode
    if debug_mode:
        print("[CS] Unloaded script.")

    obs.timer_remove(get_song_info)


def script_update(settings):
    global debug_mode
    if debug_mode:
        print("[CS] Updated properties.")

    global enabled
    global room

    if obs.obs_data_get_bool(settings, "enabled") is True:
        if (not enabled):
            if debug_mode:
                print("[CS] Enabled song timer.")

        enabled = True
    else:
        if (enabled):
            if debug_mode:
                print("[CS] Disabled song timer.")

        enabled = False

    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    room = obs.obs_data_get_int(settings, "room")


if debug_mode:
    print('[RUNNING] Server is running on port:')


while True:
    #  Wait for next request from client
    message = socket.recv()

    #  Do some 'work'
    time.sleep(1)

    if message is 'start':
        obs.obs_frontend_recording_start()
    elif message is 'stop':
        obs.obs_frontend_recording_stop()
    else:
        pass
