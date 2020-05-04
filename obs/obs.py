#
#   Server connector
#   Connects REQ socket to the web-server
#   Sends a status request to the server, expects either start, stop or something else back
#

import zmq
import obspython as obs
from time import sleep


server = "tct://192.168.1.78:5555"
context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect(server)


while True:

    socket.send(b"status")
    #  Get the reply.
    message = socket.recv()
    if message is 'start':
        obs.obs_frontend_recording_start()
    elif message is 'stop':
        obs.obs_frontend_recording_stop()
    else:
        pass
    sleep(1)
