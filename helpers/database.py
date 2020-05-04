import sqlite3
import json
from flask import g
from datetime import datetime

#  Databases connected to this project
DATABASE = '/home/pi/nurse/db/nurse.db'


# ANSWERSDB = '/db/answers.db'

# ########################################################### #
# #                   Database connections                  # #
# ########################################################### #
# get_db() and query_db() fetched from Flask Documentation https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
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


def insert_db(query, args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    c = cur.lastrowid
    cur.close()
    return c


# ########################################################### #
# #                     Teacher/Sensors                     # #
# ########################################################### #

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
    access_id = query_db('select * from examsensor where accessID = ?',
                         [card], one=True)
    if access_id is None:
        return 'No such user'
    else:
        return access_id, 'exists in db', access_id['name']


# ########################################################### #
# #                         Exams                           # #
# ########################################################### #

def get_available_exams():
    exams = query_db('SELECT * FROM exams WHERE is_active = 1', one=False)
    return exams


def get_exam_info(exam):
    exam_info = query_db('SELECT * FROM exams WHERE exam_id = ? AND is_active = 1',
                         [exam], one=True)
    if exam_info is None:
        return 'Sorry, that exam is not active or doesn\'t exists.'
    else:
        return exam_info


# ########################################################### #
# #                      Questions                          # #
# ########################################################### #

def exam_get_questions(exam):
    e = query_db('select * from examquestions where examID = ?',
                 [exam], one=False)
    return e


def get_single_question(quid):
    e = query_db('select important from examquestions where question_id = ?',
                 [quid], one=True)
    return e


def exam_get_questions_required(exam):
    e = query_db('select question_id, important from examquestions where examID = ?',
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


def check_if_minimum_is_completed(exam, min_correct):
    correct = query_db('SELECT min_correct FROM exams WHERE exam_id = ?',
                       [exam], one=True)

    c = int(correct[0])
    e = int(min_correct)
    if e >= c:
        return '1'
    else:
        return '0'


# ########################################################### #
# #                         Results                         # #
# ########################################################### #

def get_results(result_id):
    r = query_db('SELECT * FROM results WHERE res_id = ?',
                 [result_id], one=True)
    return r


def only_questions(e):
    r = query_db('SELECT question FROM examquestions WHERE examID = ?',
                 [e], one=False )
    return r


def insert_result(case_id, exam_id, answers, start_time, grade, is_exam, sensor, json):
    now = datetime.now()
    time_used = str(now - start_time)

    # Making sure everything is in the correct format before insert.
    date = str(now.strftime("%Y-%m-%d"))
    c = int(case_id)
    e = int(exam_id)
    a = str(answers)
    gr = int(grade)
    ie = int(is_exam)
    se = str(sensor)

    stu = 0
    comment = "Comments"

    con = insert_db('INSERT INTO results'
                    '(case_id, date_completed, exam_id, answers, sensor, is_exam, time_used, student, grade,'
                    'comment, start_time, stop_time, json)'

                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [c, date, e, a, se, ie, time_used, stu, gr, comment, start_time, now, json])
    return con


def get_case(x):
    case = query_db('SELECT * FROM cases WHERE case_id = ?',
                    [x], one=True)
    return case


# ########################################################### #
# #                      active exams                       # #
# ########################################################### #

def db_set_active_exam(e=None, r=None):
    if e is not None and r is not None:
        query_db('INSERT INTO active_exam (exam_id, start_time, room, recording) VALUES(?,?,?,?)',
                 [e, r], one=True)
    a = query_db('SELECT ae_id FROM active_exam WHERE room = ?',
                 [r], one=True)
    if a is not None:
        return a
    else:
        return "Error with the program or failed to get the room id, or no exam is currently ongoing in that room."


def start_new_exam(exam_id, room):
    """
    :param exam_id: gets the ID of the exam the student is currently doing.
    :param room: Gets the room ID from the tablet, setup needs to be done correctly.
    :return: Returns false if an exam is already ongoing in that room. Else inserts a new row.
    """

    if get_active_exam(room):
        return 'Exam is ongoing in that room, give this to an admin to check if room is set correctly'

    time = datetime.now()
    query_db('INSERT INTO active_exam (exam_id, start_time, room, recording) VALUES (?)',
             [exam_id, time, room, 1], one=True)
    return True


def get_active_exam(x):
    row_exists = query_db('SELECT * FROM active_exam WHERE room = ?',
                          [x], one=True)
    return row_exists


def finish_exam_close_active(room):
    # TODO: End exam in room
    #   * Check if a exam is active.
    #   * Delete the row if exists
    row_exists = query_db('SELECT * FROM active_exam WHERE room = ?',
                          [room], one=True)
    if row_exists:
        query_db('DELETE FROM active_exam WHERE room = ?',
                 [room], one=True)
    return True


def update_active_exam_waiting(room):
    query_db('UPDATE active_exam SET recording = 2 WHERE room = ?',
             [room], one=True)
    return True


# ########################################################### #
# #                       Exceptions                        # #
# ########################################################### #

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
