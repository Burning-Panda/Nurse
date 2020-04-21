#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, redirect, request, session, Response, make_response
from datetime import timedelta, datetime
import json
from werkzeug.debug import DebuggedApplication

# Import from helper files
from helpers.database import *
from helpers.reader import read


# ########################################################### #
# #                     App Config                          # #
# ########################################################### #
app = Flask(__name__)
app.secret_key = b'l>/p)$3rsEDj_C:G_6#Pr:9l345d@}'
# Sets the secret key, used for signing sessions, and making sure they are not tampered with.

# app.permanent_session_lifetime = timedelta(minutes=30)  # max time the session is stored.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
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
    Session_reset resets all unnecessary sessions which are not required to use the app.
    :return:
    """

    session_reset()
    return render_template("index.html", homepage=True)


@app.route('/exams', methods=['POST', 'GET'])
def choose_exam():
    # TODO: Check if post function is necessary.
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
    # TODO: Add random case generator.
    """
    :param exam_id: get the exam ID
    :return: the website for a single exam.
    """
    ex_info = get_exam_info(exam_id)
    case = get_case(1)
    gender = case[1]
    if gender == 1:
        g = 'Mann'
    else:
        g = 'Kvinne'

    splitter = ex_info[3].split('|')
    return render_template('exam.html', exam_id=exam_id, exam=ex_info, desc=splitter, case=case, gender=g)


@app.route('/exam/<exam>/in-progress', methods=['POST', 'GET'])
def tasks(exam):
    # TODO: Insert data into database on completion.
    """
    :param exam: gets the exam from the website
    :return: returns a list of questions related to that exam.
    """
    if request.method == "POST":
        form_data = request.form
        e = get_total_questions_available(exam)

        answer_string = ""
        for d in form_data:
            answer_string += str(form_data[d])
            answer_string += "|"
        answers = answer_string[:-1]

        # insert_result(session['case_id'], exam, answers,
        #                          session['start_time'], session['is_exam'], session['sensor'])

        # if resulting is not True:
        #    return f'Error with inserting'

        return render_template('results.html', e=exam, q=e, data=answers)

    else:
        q = exam_get_questions(exam)

        if not session.get('sensor'):
            session['start_time'] = datetime.now()
        return render_template('questions.html', question=q, exam=exam)


@app.route('/results/<result_id>')
def results(result_id):
    # TODO: Create the results page.
    #   make sure the correct students are the only ones who can read it

    #    Use with exam mode and examinees
    #    user = query_db('select * from users where username = ?',
    #                [the_username], one=True)
    #    if user is None:
    #        print 'No such user'
    #    else:
    #        print the_username, 'has the id', user['user_id']

    result = get_result(result_id)
    session_reset()
    return render_template('results.html', data=result)


@app.route('/with-sensor', methods=['GET', 'POST'])
def sensor_login():
    # TODO: Store sensor somewhere.
    #   * Sessions is a good option.

    """
    Reads the RFID reader connected to the Pi
    :return: returns 200 to the website if a card is read from the reader,
     or if there was no nothing read for 4 minutes, sends reset code to the requesting website.
    """

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
            return Response("fail", status=406, mimetype='application/json')

        session['sensor'] = sensor
        # Afterwards, returns a message to the ajax script on the website, telling it to continue.
        return Response("done", status=200, mimetype='application/json')


# ########################################################### #
# #                  ONLY FOR OBS STUDIO!                   # #
# ########################################################### #

@app.route('/obs-rec-status-change/<room>')
def obs_status_change(room):
    # TODO: Check return codes
    #   make sure OBS can read them

    """
    possible return codes:
    start, stop, Waiting
    :return: code for the obs to read.
    """

    active = get_active_exam(room)

    if active is not None or active[4] is not 2:
        if active[4] is 1:
            update_active_exam_waiting(room)
            return f"start"
        else:
            return f"stop"
    else:
        # as long as recording status is 2 or none, it will display this.
        # OBS will not do anything as long as this is shown
        return f"waiting"


# TODO
# ########################################################### #
# #                    Admin panel!                         # #
# ########################################################### #

@app.route("/admin")
def admin_config():
    # TODO: Add admin page
    return f'Admin page'


@app.route("/tablet-config")
def tablet_config():
    # TODO: Add  a tablet config page
    #   * needs a room setup
    #   * sessions
    #       - session["room"] = 1
    #   * Form data handler
    return f'tablet Config'


@app.route("/admin/exams")
def admin_exams():
    # TODO: Add admin exams page
    return f'Admin Exams'


@app.route("/admin/exams/new")
def admin_exams_new():
    # TODO: Add exams add new page
    return f'New exam'


@app.route("/admin/exams/edit/<ex_id>")
def admin_exam_edit(ex_id):
    # TODO: Add exams edit exam
    return f'Edit exams'


# Sensors
@app.route("/admin/sensors")
def admin_sensors():
    # TODO: Add admin page for sensors
    #   Check only active or everyone
    return f'Sensor'


@app.route("/admin/sensors/new")
def admin_new_sensor(sensor_id):
    # TODO: Add a way to add new sensors
    return True


@app.route("/admin/sensors/edit/<sensor_id>")
def admin_sensors_edit_sensor(sensor_id):
    # TODO: Add a way to edit the sensors or delete
    return True


# ########################################################### #
# #                     Functions!                          # #
# ########################################################### #

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
    return True


@app.errorhandler(404)
def not_found():
    # TODO: Error handler
    #  Status: Does not work!!!!
    """Page not found."""
    return make_response(render_template("404.html"), 404)


# Starts the app on local network.

if __name__ == '__main__':
    app.run(host='0.0.0.0')
