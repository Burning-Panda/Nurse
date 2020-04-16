import sqlite3
import json
from flask import g

#  Databases connected to this project
DATABASE = '/home/pi/nurse/db/nurse.db'

# ANSWERSDB = '/db/answers.db'


# def get_db_answers():
#    answer = getattr(g, '_database', None)
#    if answer is None:
#        answer = g._database = sqlite3.connect(ANSWERSDB)
#    return answer


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


def sensors_list(x=None, i_a=False):
    if x is None:
        get_sen = query_db('select * from examsensor')
    else:
        if i_a is True:
            get_sen = query_db('select * from examsensor where is_active= 1;')
        else:
            get_sen = query_db('select * from examsensor')
    return get_sen


def sensor_exists(card):
    accessID = query_db('select * from examsensor where accessID = ?',
                        [card], one=True)
    if accessID is None:
        return 'No such user'
    else:
        return accessID, 'exists in db', accessID['name']


def get_available_exams():
    exams = query_db('select * from exams where is_active = 1;')
    return exams


def get_exam_info(exam):
    exam_info = query_db('SELECT * FROM exams WHERE exam_id = ? AND is_active = 1',
                         [exam], one=True)
    if exam_info is None:
        return 'Sorry, that exam is not active or doesn\'t exists.'
    else:
        return exam_info


def exam_get_questions(exam):
    e = query_db('select * from examquestions where examID = ?',
                 [exam], one=False)
    return e


def get_total_questions_available(x):
    e = query_db('SELECT COUNT(*) FROM examquestions WHERE examID = ?;',
                 [x])
    return e


def get_question_ids(exam):
    ids = query_db('SELECT question_id FROM examquestions WHERE examID = ?',
                   [exam], one=False)
    return ids


def db_set_active_exam(e=None, r=None):
    if e is not None and r is not None:
        query_db('INSERT INTO active_exam (exam_id, start_time, room) VALUES(?,?)',
                 [e], [r], one=True)
    a = query_db('SELECT ae_id FROM active_exam WHERE room = ?',
                 [r], one=True)
    if a is not None:
        return a
    else:
        return "Error with the program or failed to get the room id, or no exam is currently ongoing in that room."


def get_case(x):
    case = query_db('SELECT * FROM cases WHERE case_id = ?',
                    [x], one=True)
    return case


def finish_exam_close_active(room):
    # TODO: End exam in room
    #   * Check if a exam is active.
    #   * Delete the row if exists
    row_exists = query_db('SELECT * FROM active_exam WHERE room = ?',
             [room], one=True)
    if row_exists:
        query_db('DELETE FROM active_exam WHERE room = ?',
                 [room], one=True)


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
