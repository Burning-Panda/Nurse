#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import sqlite3
from flask import g

DATABASE = '/home/pi/nurse/db/nurse.db'


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
room = 1


def get_db():
    exam_db = getattr(g, '_database', None)
    if exam_db is None:
        exam_db = g._database = sqlite3.connect(DATABASE)
    return exam_db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_active_exam(x):
    row_exists = query_db('SELECT * FROM active_exam WHERE room = ?',
                          [x], one=True)
    return row_exists


while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    active = get_active_exam(room)
    if active is None:
        #  Send reply back to client
        socket.send(b"nothing")
    elif active[5] is 'start':
        socket.send(b"start")
    elif active[5] is 'stop':
        socket.send(b"stop")
    else:
        socket.send(b"nothing")
