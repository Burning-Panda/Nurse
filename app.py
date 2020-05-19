#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, url_for, redirect, request, session, Response, make_response, flash, send_from_directory
from datetime import timedelta, datetime
import json
import uuid

# Import from helper files
from helpers.database import *
from helpers.reader import read
from obs.obsws import obs_connector
from helpers.pdf import render

# ########################################################### #
# #                     App Config                          # #
# ########################################################### #
app = Flask(__name__)
app.secret_key = b'aFvAUaVyaxW7ENbT4S2HDyQW3n0EEGnJYtehL9kG29LUaYWu56g4-KE5aZl3ck4xJkXEku4PoduaYK3k'
app.config["SECRET_KEY"] = 'aFvAUaVyaxW7ENbT4S2HDyQW3n0EEGnJYtehL9kG29LUaYWu56g4-KE5aZl3ck4xJkXEku4PoduaYK3k'
# Sets the secret key, used for signing sessions, and making sure they are not tampered with.

app.permanent_session_lifetime = timedelta(days=365)  # max time the session is stored.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

auth_key = 'Yv326fIgqRoZocoYo5jjU0OAR_rJe6LpzCkbAr6F'
# End Config


# ########################################################### #
# #                    Main application                     # #
# ########################################################### #
@app.route('/')
@app.route('/index')
@app.route('/home')
def splash():
    # TODO: Rework homepage to look good.
    #   * Does it need a "homepage"?
    #   * Is this only a splash and prep page?

    """
    Session_reset(): resets all unnecessary sessions which are not required to use the app.
    tablet settings are not reset, and should only be changed by an administrator.
    Its done this way so it can be scaled up to more rooms and still use the same system.
    :return:
    """

    session_reset()
    if session.get('room'):
        session['room'] = 1

    session['is_exam'] = 1

    return render_template("index.html", homepage=True)


@app.route('/exams', methods=['POST', 'GET'])
def choose_exam():
    # TODO:
    #   * Waiting for Chris / Kay
    """
    Gets the website for all exams, checks database for what exams is available.
    if :Method GET:  Gets the website and loads exams from the database.
    if :method post: selects the exam and continues to the next website.
    :return:
    """

    if request.method == "POST":
        form_data = request.form
        return redirect(url_for('exam_choice', exam_id=form_data['exams']))
    else:
        if session.get('sensor'):
            s = session['sensor']
        else:
            s = 'None'
        avb_tests = get_available_exams()
        return render_template('exams.html', exams=avb_tests, sensor=s)


@app.route('/exam/<int:exam_id>')
def exam_choice(exam_id):
    # TODO:
    #   * Add random case generator.
    #   * Wait for Chris / Kay
    """
    :param exam_id: get the exam ID
    :return: the website for a single exam.
    """
    ex_info = get_exam_info(exam_id)
    case = get_case(1)
    session['case'] = 1

    gender = case[1]
    if gender == 1:
        g = 'Mann'
    else:
        g = 'Kvinne'

    splitter = ex_info[3].split('|')
    return render_template('exam.html', exam_id=exam_id, exam=ex_info, desc=splitter, case=case, gender=g)


@app.route('/exam/<int:exam>/in-progress', methods=['POST', 'GET'])
def tasks(exam):
    """
    :param exam: gets the exam from the website link eg /exam/1/in-progress
    :return: returns a list of questions related to that exam.
    :return: On post, redirects the user to the results page.
    """
    q = exam_get_questions(exam)
    get_room = session.get('room')

    if request.method == "POST":
        form_data = request.form

        # counts points from exam, each question is worth 1 point. if the total amount is less than the required for the
        # exam, returns a 0
        count = 0
        for c in form_data:
            count = count + int(form_data[c])

        # Checking if enough of the answers are correct to pass
        min_correct = int(check_if_minimum_is_completed(exam, count))

        answer_string = ""
        for d in form_data:
            answer_string += str(form_data[d])
            answer_string += "|"
        # Removing the last | from the string before putting it into the db.
        answers = answer_string[:-1]

        # If these sessions don't exists, or is None, sets them to 0 to avoid errors.
        if session.get('sensor') is None:
            session['sensor'] = 0
        if session.get('is_exam') is None:
            session['is_exam'] = 0

        # gets the session data and stores it into a variable. Lessens chance of errors.
        case_id = session['case']
        st_time = session['start_time']
        ie = session['is_exam']
        active_sensor = session['sensor']

        # Dump and loading of data for easier validation
        # This was the only way to make it work correctly without errors.
        dump = json.dumps(form_data)
        load = json.loads(dump)
        dict_keys = getList(load)

        # Runs through the answers to validate if user has passed.
        # it is done like this for the database to get the data correctly.
        # To fix database/python errors, i had to convert the e variable to a string
        # I also had to do it to make sure the comparison works like it should, the answers needed to be integer and
        # not strings
        checker = 0
        for e in dict_keys:
            single_question = get_single_question(str(e))
            sq = int(single_question[0])
            answ = int(form_data[e])
            if sq is 1 and answ is not 1:
                checker += 1
            else:
                checker += 0

        # Checking if they passed both validators
        if checker is 0 and min_correct is 1:
            grade = 1
        else:
            grade = 0
        text_grade = str(grade)

        # Inserts result and returns the last inserted ID for the redirection to the next page.
        ins = insert_result(case_id, exam, answers, st_time, text_grade, ie, active_sensor, dump)

        obs_status_change(get_room, 'stop')
        # if grade is 0:
        #    redirect(url_for('comment', result_id=ins))
        # else:
        return redirect(url_for('results', result_id=ins))
        # return render_template('results.html', e=exam, q=e, data=answers, count=count, c=min_correct, i=ins)

    else:
        # Saves the time locally on the browser and renders the exam questions template.
        # Time is used for validation and results
        obs_status_change(get_room, 'start')
        session['start_time'] = datetime.now()
        return render_template('questions.html', question=q, exam=exam)


@app.route('/results/<result_id>/comment')
def comment(result_id):
    # TODO:
    #  * Wait for correct template from Chris / Kay
    """
    Comments will be written here.
    Comment is stored related to one specific student.
    :param result_id: Gets the result ID from the previous page.
    :return: After comment is written, sends the user to the results page.
    """
    # Check if the user wants a comment
    if request.method == "POST":
        form_data = request.form
        want_comment = form_data['comment']
        result_with_comment(str(want_comment))
        return redirect(url_for(results, id=result_id))
    else:
        # return render_template('comment.html', id=result_id)
        return render_template('results.html')  # , id=result_id)


@app.route('/results/<result_id>')
def results(result_id):
    # TODO: Create the results page.
    #   * make sure the correct students are the only ones who can read it
    #     scan card to access?

    result = get_single_result(result_id)
    answers = result[4].split('|')

    exam_info = get_exam_info(result[3])
    info_to_student = exam_info[3].split('|')

    questions = exam_get_questions(result[3])

    zipped = zip(questions, answers)

    # Simplifies the grade for reading purpose.
    if result[9] is not 1:
        grade = 'FAILED'
    else:
        grade = 'PASSED'

    session_reset()
    return render_template('results.html', r=result, exam_info=info_to_student, p=zipped, grade=grade)


# ########################################################### #
# #                       Scanning Card                     # #
# ########################################################### #
"""
    Reads the RFID reader connected to the Pi
    :return: returns 200 to the website if a card is read from the reader,
     or if there was no nothing read for 4 minutes, sends reset code to the requesting website.
"""


@app.route('/scan/sensor', methods=['GET', 'POST'])
def sensor_login():
    # TODO:
    #    * Check why scanning doesn't work...
    if request.method == 'GET':
        return render_template('loader.html')

    if request.method == 'POST':
        # waits for a card to be read by the scanner.
        sensor = read()
        while sensor is None:
            # making sure a card is actually read.
            # If nothing is done
            pass

        if sensor is False:
            flash('You did not scan your card in time.')
            return Response("fail", status=406, mimetype='application/json')

        session['sensor'] = sensor[0]
        # Afterwards, returns a message to the ajax script on the website, telling it to continue.
        flash('Your card was scanned successfully!')
        return Response("done", status=200, mimetype='application/json')
    else:
        return Response("fail", status=406, mimetype='application/json')


@app.route('/scan/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        return render_template('loader.html')

    if request.method == 'POST':
        student = read()
        while student is None:
            pass

        if student is False:
            flash('You did not scan your card in time.')
            return Response("fail", status=406, mimetype='application/json')

        session['student'] = student
        flash('Your card was scanned successfully!')
        return Response("done", status=200, mimetype='application/json')


# ########################################################### #
# #                  ONLY FOR OBS STUDIO!                   # #
# ########################################################### #

def obs_status_change(room_id, command):
    room = get_room_info(room_id)
    ip = str(room[3])
    firewall = int(room[4])
    password = str(room[5])
    obs_connector(ip, firewall, password, command)
    return True


# TODO
# ########################################################### #
# #                    Admin panel!                         # #
# ########################################################### #

@app.route("/admin")
def admin_main():
    ax = count_all_completed_exams()
    l30d = count_all_last_30_days()
    l24d = count_last_24_hours()

    websiteStrings = []

    websiteStrings.append(ax[0])
    websiteStrings.append(l30d[0])
    websiteStrings.append(l24d[0])
    websiteStrings.append(ax[0])

    countL30D = last_30_day_count_per_day()

    return render_template('admin/index.html', ws=websiteStrings, last30days=countL30D)


@app.route("/tablet-config", methods=['GET', 'POST'])
def tablet_config():
    if request.method == 'POST':
        session['room'] = request.form.get('roomNbR')
        flash('Aktiv Rom nummer er lagret!', 'success')
        room_list = obs_rooms_available()
        return render_template('admin/tablet-control.html', rooms=room_list)
    else:
        room_list = obs_rooms_available()
        return render_template('admin/tablet-control.html', rooms=room_list)


@app.route("/admin/exams", methods=['GET', 'POST'])
def admin_exams():
        aex = get_active_exams()
        dex = get_deactivated_exams()
        return render_template('admin/exams.html', aex=aex, dex=dex)


@app.route("/admin/exams/<int:eid>/<int:funct>", methods=['GET'])
def admin_exams_switch(eid, funct):
    error = None
    if funct == 1:
        activate_exam(eid)
        flash(f'You successfully activated a exam with id: {eid}', 'success')
        return redirect(url_for('admin_exams'))
    elif funct == 0:
        deactivate_exam(eid)
        flash(f'You successfully deactivated a exam with id: {eid}', 'success')
        return redirect(url_for('admin_exams'))
    else:
        flash(f'Server error, do not worry. Please try again.', 'error')
        return redirect(url_for('admin_exams'))


@app.route("/admin/exams/new")
def admin_exams_new():
    if request.method == 'POST':
        pass
    # TODO: Add exams add new page

    return render_template('admin/view-exam.html')


@app.route("/admin/exams/new/post")
def admin_exams_new_post():
    return redirect(url_for('admin_exams'))


@app.route("/admin/exams/edit/<ex_id>")
def admin_exam_edit(ex_id):
    # TODO: Add exams edit exam
    return render_template('admin/view-exam.html', needs_hidden_field=True)


# Sensors
@app.route("/admin/users")
def admin_users():
    # TODO: Add admin page for sensors
    #   Check only active or everyone
    return render_template('admin/users.html')


@app.route("/admin/users/new")
def admin_new_users():
    # TODO: Add a way to add new Users
    return render_template('admin/users.html')


@app.route("/admin/users/edit/<uid>")
def admin_user_edit(uid):
    # TODO: Add a way to edit the Users or delete
    return render_template('admin/users.html')


@app.route("/admin/results")
def admin_responses():
    r = get_all_results()
    return render_template('admin/answers.html', results=r)


@app.route("/admin/results/view/<rid>")
def admin_responses_single(rid):
    result = get_single_result(rid)
    answers = result[4].split('|')

    exam_info = get_exam_info(result[3])
    info_to_student = exam_info[3].split('|')

    questions = exam_get_questions(result[3])

    zipped = zip(questions, answers)

    return render_template('admin/view-answers.html', r=result, exam_info=info_to_student, p=zipped)


@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == "POST" and session.get('is_auth') is None:
        log = request.form
        q = admin_login(log[0], log[1])
        if q is True:
            session['is_auth'] = auth_key
        return redirect(url_for(admin_main))
    else:
        if session.get('is_auth'):
            session.pop('is_auth', None)

        return render_template('admin/signin.html')


# ########################################################### #
# #                     Functions!                          # #
# ########################################################### #

def login_val():
    if session.get('is_auth') == auth_key:
        return True
    else:
        return False


def getList(dict):
    # Code fetched from GeeksForGeeks at https://www.geeksforgeeks.org/python-get-dictionary-keys-as-a-list/
    list = []
    for key in dict.keys():
        list.append(key)

    return list


def selected_exam(exam, sensor):
    """
    :param exam:   The exam ID
    :param sensor: The sensor ID if selected
    :return: True  or False
    """
    session['exam'] = exam
    if sensor is not False:
        session['is_exam_sensor'] = sensor

    insert = db_set_active_exam()
    if insert is None:
        return False
    else:
        session['active_exam'] = insert
        return True


# ########################################################### #
# #                     Full app reset!                     # #
# ########################################################### #
@app.route('/install', methods=['GET'])
def first_time_install():
    if session.get('tablet_unique_id') is None:
        unique = uuid.uuid1()
        session['tablet_unique_id'] = unique
        add_to_active_tablets(unique)
    return redirect(url_for('splash'))


@app.route('/reset', methods=['GET'])
def reset_tablet():
    session_reset()
    if session.get('tablet_unique_id'):
        delete_from_active_tablets(session.get('tablet_unique_id'))
        session.pop('tablet_unique_id', None)
    return redirect(url_for('first_time_install'))


def session_reset():
    # TODO: Add all sessions into this reset.
    """
    Quick reset of all websites sessions.
    Checks if a session is set, and if it is, resets it.
    :return: True
    """
    if session.get('sensor'):
        session.pop('sensor', None)
    if session.get('active_exam'):
        session.pop('active_exam', None)
    if session.get('start_time'):
        session.pop('start_time', None)
    if session.get('is_exam'):
        session.pop('is_exam', None)
    if session.get('case'):
        session.pop('case', None)
    return True


@app.errorhandler(404)
def not_found():
    # TODO: Error handler
    #  Status: Does not work!!!!
    """Page not found."""
    return make_response(render_template("404.html"), 404)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Starts the app on local network.
if __name__ == '__main__':
    app.run(host='0.0.0.0')
