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


def _db(query, args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()
    return True


# ########################################################### #
# #                     Teacher/Sensors                     # #
# ########################################################### #

def sensors_list(x=None, i_a=False):
    if x is None:
        get_sen = query_db('select * from users WHERE userType = 1')
    else:
        if i_a is True:
            get_sen = query_db('select * from users where userType = 1 and isActive = 1;')
        else:
            get_sen = query_db('select * from users WHERE userType = 1')
    return get_sen


def get_single_sensor(s):
    q = query_db('SELECT * FROM users WHERE user_id = ?',
                 [s], one=True)
    return q


def get_sensor_from_card(card):
    q = query_db('SELECT user_id, first_name, last_name FROM users WHERE card_number = ?',
                 [card], one=True)
    return q


def sensor_exists(card):
    access_id = query_db('select * from users where card_number = ?',
                         [card], one=True)
    if access_id is None:
        return 'No such user'
    else:
        return access_id, 'exists in db', access_id['name']


# ########################################################### #
# #                      Students                           # #
# ########################################################### #

def get_student_info_from_card(card):
    q = query_db('SELECT student_id, first_name, last_name FROM users WHERE card_number = ?',
                 [card], one=True)
    return q


def get_users_name(card):
    q = query_db('SELECT first_name, last_name FROM users WHERE card_number = ?',
                 [card], one=True)
    return q


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

def get_single_result(result_id):
    r = query_db('SELECT results.res_id, results.case_id, results.date_completed, results.exam_id, results.answers, '
                 'results.sensor, results.is_exam, results.time_used, results.student, results.grade, '
                 'results.comment, results.start_time, results.stop_time, results.json, exams.shortname, '
                 'exams.max_time, users.first_name, users.last_name FROM results LEFT JOIN exams on '
                 'results.exam_id = exams.exam_id LEFT JOIN users on results.student = users.user_id '
                 'WHERE results.res_id = ?',
                 [result_id], one=True)
    return r


def only_questions(e):
    r = query_db('SELECT question FROM examquestions WHERE examID = ?',
                 [e], one=False)
    return r


def insert_result(case_id, exam_id, answers, start_time, grade, is_exam, sensor, json, student):
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
    stu = int(student)

    comment = None

    con = insert_db('INSERT INTO results'
                    '(case_id, date_completed, exam_id, answers, sensor, is_exam, time_used, student, grade,'
                    'comment, start_time, stop_time, json)'

                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [c, date, e, a, se, ie, time_used, stu, gr, comment, start_time, now, json])
    return con


def result_with_comment(comment, res_id):
    _db('UPDATE results SET comment = ? WHERE res_id = ?',
        [comment, res_id])


def get_case(x):
    case = query_db('SELECT * FROM cases WHERE case_id = ?',
                    [x], one=True)
    return case


# ########################################################### #
# #                      active exams                       # #
# ########################################################### #

def db_set_active_exam(e=None, r=None):
    if e is not None and r is not None:
        query_db('INSERT INTO active_exam (exam_id, start_time, room) VALUES(?,?,?)',
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
    query_db('INSERT INTO active_exam (exam_id, start_time, room) VALUES (?)',
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
# #                       OBS ROOMS                         # #
# ########################################################### #
def obs_rooms_available():
    q = query_db('SELECT * FROM rooms')
    return q


def add_new_room_to_db(room_name, room, ip, firewall, password):
    _db('INSERT INTO rooms(roomName, room, ip, firewall, password) VALUES (?, ?, ?, ?, ?)',
        [room_name, room, ip, firewall, password])
    return True


def get_room_info(room_id):
    q = query_db('SELECT * FROM rooms WHERE room = ?',
                 [room_id], one=True)
    return q


def delete_obs_room_db(room_id):
    _db('DELETE FROM rooms WHERE server_id = ?',
        [room_id])
    return True


# ########################################################### #
# #                      Admin pages                        # #
# ########################################################### #
def admin_login(u, m):
    q = query_db('SELECT user_id, userType, password FROM users WHERE user_id = ?'
                 [u], one=True)
    if q[1] is 3 and m is q[2]:
        return True
    else:
        return False


# Dashboard
def count_all_completed_exams():
    count = query_db('SELECT COUNT(*) FROM results')
    return count[0]


def count_all_last_30_days():
    count = query_db('SELECT count(*) FROM results WHERE datetime(start_time) >= datetime("now", "-30 days")')
    return count[0]


def count_last_24_hours():
    count = query_db('SELECT count(*) FROM results WHERE datetime(start_time) >= datetime("now", "-24 hours")')
    return count[0]


def count_passed_exams():
    count = query_db('SELECT count(*) FROM results WHERE is_exam = 1 AND grade = 1')
    return count[0]


def last_30_day_count_per_day():
    count = []
    for x in range(30):
        if x is 0:
            count.append(query_db('SELECT count(*) FROM results WHERE date(date_completed) == date("now")', one=True))
        elif x is 1:
            day = f"-{x} day"
            count.append(query_db('SELECT count(*) FROM results WHERE date(date_completed) == date("now", ?)',
                                  [day], one=True))
        else:
            day = f"-{x} days"
            count.append(query_db('SELECT count(*) FROM results WHERE date(date_completed) == date("now", ?)',
                                  [day], one=True))

    return count


# Exams
def get_active_exams():
    q = query_db('SELECT * FROM exams WHERE is_active = 1')
    return q


def get_deactivated_exams():
    q = query_db('SELECT * FROM exams WHERE is_active = 0')
    return q


def activate_exam(x):
    insert_db('UPDATE exams SET is_active = 1 WHERE exam_id = ?',
              [x])


def deactivate_exam(x):
    insert_db('UPDATE exams SET is_active = 0 WHERE exam_id = ?',
              [x])


def admin_get_exam_info(ex_id):
    q = query_db('SELECT * FROM exams WHERE exam_id = ?',
                 [ex_id], one=True)
    return q


def update_questions_if_edited(key, val):
    _db('UPDATE examquestions SET question = ? WHERE question_id = ?',
        [val, key])
    return True


def update_important_questions(key, val):
    _db('UPDATE examquestions SET important = ? WHERE question_id = ?',
        [val, key])
    return True


def admin_add_new_exam(name, desc, outfit, time, mincorr):
    q = insert_db('INSERT INTO exams(shortname, info, outfit, max_time, dateadded, is_active, min_correct)'
                  'VALUES (?,?,?,?,date("now"),1,?)',
                  [name, desc, outfit, time, mincorr])
    return q


def add_new_questions(exam, question, important):
    q = insert_db('INSERT INTO examquestions(examID, question, important)'
                  'VALUES (?,?,?)',
                  [exam, question, important])
    return q


def db_delete_question(qid):
    _db('DELETE FROM examquestions WHERE question_id = ?',
        [qid])
    return True


def update_exam_info(name, desc, outfit, time, mincorr, eid):
    _db('UPDATE exams SET shortname = ?, info = ?, outfit = ?, max_time = ?, min_correct = ?'
        'WHERE exam_id = ?',
        [name, desc, outfit, time, mincorr, eid])
    return True


# Results
def get_all_results():
    q = query_db('select results.res_id, results.date_completed, results.exam_id, results.time_used, results.student, '
                 'results.grade, exams.exam_id, exams.shortname, exams.max_time FROM results LEFT JOIN exams on '
                 'results.exam_id = exams.exam_id')
    return q


# Users
def all_student_users():
    q = query_db('SELECT * FROM users WHERE userType=1 ORDER BY isActive DESC')
    return q


def all_teacher_users():
    q = query_db('SELECT * FROM users WHERE userType>=2 ORDER BY isActive DESC')
    return q


def get_user_types():
    q = query_db('SELECT id, name FROM userTypes')
    return q


def edit_user(uid):
    q = query_db('SELECT * FROM users WHERE user_id = ?',
                 [uid], one=True)
    return q


def admin_update_user(fname, lname, utype, email, pw, studid, card):
    _db('INSERT INTO users(card_number, student_id, first_name, last_name, student_mail, '
        'userType, password)'
        'VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
        [card, studid, fname, lname, email, utype, pw])
    return None


def activate_user(x):
    insert_db('UPDATE users SET isActive = 1 WHERE user_id = ?',
              [x])


def deactivate_user(x):
    insert_db('UPDATE users SET isActive = 0 WHERE user_id = ?',
              [x])


# ########################################################### #
# #                      Registration                       # #
# ########################################################### #
def register_new_user(fname, lname, utype, email, pw, studid):
    q = insert_db('INSERT INTO users(card_number, student_id, first_name, last_name, student_mail, exams_taken,'
                  'exams_passed, exams_failed, practice_exams_done, isActive, userType, password)'
                  'VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                  [0, studid, fname, lname, email, 0, 0, 0, 0, 1, utype, pw])
    if q is None:
        return False
    return q


def add_student_card(user, card):
    _db('UPDATE users SET card_number = ? WHERE user_id = ?',
        [card, user])
    return True


def add_student_card_with_studid(card, studid):
    stu = int(studid)
    nbr = str(card)
    _db('UPDATE users SET card_number = ? WHERE student_id = ?',
        [nbr, stu])
    return True


def check_if_identity_exists(sid):
    q = query_db('SELECT user_id, card_number, student_id FROM users WHERE student_id = ?',
                 [sid], one=True)
    if q and q[1] is 0:
        return True
    else:
        return False


def card_exists_already(card):
    q = query_db('SELECT card_number FROM users WHERE card_number = ?',
                 [card], one=True)
    if q:
        return True
    else:
        return False


# ########################################################### #
# #                        install                          # #
# ########################################################### #

def add_to_active_tablets(unique):
    insert_db('INSERT INTO active_tablets(date, is_active, uuid)'
              'VALUES(date("now"), 1, ?)',
              [unique])
    return None


def delete_from_active_tablets(unique):
    insert_db('DELETE FROM active_tablets WHERE uuid = ?',
              [unique])
    return True


# ########################################################### #
# #                       Exceptions                        # #
# ########################################################### #

def hidden_delete_function(x):
    _db('DELETE FROM exams WHERE exam_id = ?',
        [x])
    _db('DELETE FROM examquestions WHERE examID = ?',
        [x])
    return True


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
