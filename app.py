#!/usr/bin/env python3
# -*- coding: ISO-8859-1 -*-
import os
from flask import Flask, render_template, url_for, redirect, request, session, Response, make_response, flash, \
    send_from_directory
from datetime import timedelta, datetime, date
import json
import uuid

# Import from helper files
from helpers.database import *
from helpers.reader import read
from obs.obsws import obs_connector

# This function is not yet ready.
# from helpers.pdf import render

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
app.debug = False

for_testing_purpose = False


# ########################################################### #
# #                    Main application                     # #
# ########################################################### #
@app.route('/test')
def this_testing():
    a = session.get('tablet_token')
    return str(a)


@app.route('/')
@app.route('/index')
@app.route('/home')
def splash():
    """
        Session_reset(): resets all unnecessary sessions which are not required to use the app.
        tablet settings are not reset, and should only be changed by an administrator.
        Its done this way so it can be scaled up to more rooms and still use the same system.
        :return:
    """
    no_room_msg = 'Ingen rom er valgt, venligst gi denne padden til Hans Martin Lilleby'

    if session.get('tablet_token') is None:
        session['tablet_token'] = uuid.uuid4()

    is_active = tablet_settings(str(session.get('tablet_token')))
    if is_active is False:
        flash(no_room_msg)
    else:
        session['room'] = is_active

    if session.get('room') is None:
        flash(no_room_msg)

    session_reset()
    session['is_exam'] = 0

    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=365)
    return render_template("index.html", homepage=True)


@app.route('/with/sensor/active')
def with_sensor_function():
    session['is_exam'] = 1
    return redirect(url_for('user_login', opt=2))


@app.route('/exams', methods=['GET'])
def choose_exam():
    """
    Gets the website for all exams, checks database for what exams is available.
    if :Method GET:  Gets the website and loads exams from the database.
    if :method post: selects the exam and continues to the next website.
    :return:
    """

    if session.get('room') is None:
        flash('Ingen rom er valgt, venligst gi denne padden til Hans Martin Lilleby')
        return redirect(url_for('splash'))

    if session.get('sensor'):
        s = session['sensor']
        sens_name = get_users_name(session['sensor'])
    else:
        s = 'None'
        sens_name = ['', '']

    if session.get('student'):
        st = session['student']
        stu_name = get_users_name(session['student'])
    else:
        st = 'None'
        stu_name = ['', '']

    avb_tests = get_available_exams()

    time_c = []
    for x in avb_tests:
        conv = convert_time(x[5])
        conv = conv.strftime('%M Minutter')
        time_c.append(conv)

    tot_question = []
    for x in avb_tests:
        i = count_max_questions(x[0])
        tot_question.append(i[0])

    zip_tests = zip(avb_tests, time_c, tot_question)

    return render_template('exams.html', exams=zip_tests, sen_check=s, stu_check=st, sensor=sens_name, student=stu_name)


@app.route('/exam/<int:exam_id>')
def exam_choice(exam_id):
    """
    :param exam_id: get the exam ID
    :return: the website for a single exam.
    """
    ex_info = get_exam_info(exam_id)
    case = get_case(1)
    session['case'] = 1

    time = ex_info[5].split(':')
    time = time[1]

    gender = case[1]
    if gender == 1:
        g = 'Mann'
    else:
        g = 'Kvinne'

    count = count_max_questions(exam_id)

    splitter = ex_info[3].split('|')
    return render_template('exam.html', exam_id=exam_id, exam=ex_info, desc=splitter, case=case, gender=g,
                           time=time, count=count[0])


@app.route('/exam/<int:exam>/in-progress/<video>', methods=['POST', 'GET'])
def tasks(exam, video):
    """
    :param video:
    :param exam: gets the exam from the website link eg /exam/1/in-progress
    :return: returns a list of questions related to that exam.
    :return: On post, redirects the user to the results page.
    """
    q = exam_get_questions(exam)
    exam_basic_info = get_exam_short_info(exam)
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
        if session.get('student') is None:
            student = 0
        else:
            student = get_student_nbr_from_card(session.get('student'))

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
        ins = insert_result(case_id, exam, answers, st_time, text_grade, ie, active_sensor, dump, student)

        if student != 0:
            update_user_stats(session.get('student'), grade, session.get('is_exam'))

        if video == 1:
            obs_status_change(get_room, 'stop')

        return redirect(url_for('comment', result_id=ins))

    else:
        # Saves the time locally on the browser and renders the exam questions template.
        # Time is used for validation and results
        if video == 1:
            obs_status_change(get_room, 'start')
        session['start_time'] = datetime.now()
        return render_template('questions.html', question=q, exam=exam_basic_info)


@app.route('/results/<result_id>/comment', methods=['GET', 'POST'])
def comment(result_id):
    """
    Comments will be written here.
    Comment is stored related to one result.
    :param result_id: Gets the result ID from the previous page.
    :return: After comment is written, sends the user to the results page.
    """
    # Adds the comments to the result.
    if request.method == "POST":
        form_data = request.form

        dump = json.dumps(form_data)
        result_with_comment(dump, result_id)

        return redirect(url_for('results', result_id=result_id))

    else:
        return render_template('comment.html', r=result_id)


@app.route('/results/<result_id>')
def results(result_id):
    result = get_single_result(result_id)
    answers = result[4].split('|')
    comments = json.loads(result[10])

    exam_info = get_exam_info(result[3])
    info_to_student = exam_info[3].split('|')
    if result[5] is not '0':
        sensor = get_sensor_from_card(result[5])
    else:
        sensor = None

    questions = exam_get_questions(result[3])

    zipped = zip(questions, answers)

    # Concerts the date to the correct format, and can be used with the strftime function
    conv_dated = convert_date(result[2])
    # Changes the format to what we want it to look like.
    dated = conv_dated.strftime("%d %b, %Y")

    time_conv = convert_time(result[7])
    time_used = time_conv.strftime('%M Minutter og %S Sekunder')

    stud_info = get_student_info_from_card(result[8])

    # Simplifies the grade for reading purpose.
    if result[9] is not 1:
        grade = 'IKKE BESTÅTT'
    else:
        grade = 'BESTÅTT'

    session_reset()

    return render_template('results.html', r=result, exam_info=info_to_student, exam=exam_info[1], date=dated, p=zipped,
                           grade=grade, sensor=sensor, time=time_used, comment=comments, student=stud_info)


# ########################################################### #
# #                       Scanning Card                     # #
# ########################################################### #
"""
    Reads the RFID reader connected to the Pi
    :return: returns 200 to the website if a card is read from the reader,
     or if there was no nothing read for 4 minutes, sends reset code to the requesting website.
"""


@app.route('/scan/<int:opt>', methods=['GET', 'POST'])
def user_login(opt):
    """
    :param opt: The option for what user we are looking for. Student 1 or teacher 2.
    :return:
    """
    if request.method == 'GET':
        return render_template('loader.html', option=opt)

    if request.method == 'POST':
        # waits for a card to be read by the scanner.
        reader = read()

        while reader is None:
            # making sure a card is actually read.
            # If nothing is done
            pass

        if reader is False:
            flash('Du skannet ikke kortet ditt i tide.')
            return Response("Request Timeout", status=408, mimetype='application/json')

        # makes sure the card exist in our database.
        if card_exists_already(reader[0]) is False:
            # flash('This card doesn\'t exists in our database, please register as a new user.')
            flash('Dette kortet finnes ikke i vår database. Registrer deg som ny bruker')
            return Response('Not Found', status=404, mimetype='application/json')

        if opt is 2:
            session['sensor'] = reader[0]
        elif opt is 1:
            session['student'] = reader[0]
        else:
            flash('Error, How did you even access this?')
            return Response("Forbidden", status=403, mimetype='application/json')

        # Afterwards, returns a message to the ajax script on the website, telling it to continue.
        flash('Your card was scanned successfully!')
        return Response("done", status=200, mimetype='application/json')
    else:
        return Response("Not Acceptable", status=406, mimetype='application/json')


# ########################################################### #
# #                       Registration                      # #
# ########################################################### #

@app.route('/register', methods=['GET', 'POST'])
def register_new_student():
    if request.method == 'POST':
        data = request.form
        fname = data['fornavn']
        lname = data['etternavn']
        utype = 1
        email = data['epost']

        pw = 0
        studid = data['studid']

        new_user = register_new_user(fname, lname, utype, email, pw, studid)
        return redirect(url_for('register_new_student_card', user=new_user))
    return render_template("register.html")


@app.route('/register/card/<user>', methods=['GET', 'POST'])
def register_new_student_card(user):
    order = 2
    return render_template('card_fixer.html', type=order, aids=user)


@app.route('/fix/<order>', methods=['GET', 'POST'])
def studid_fix_card(order):
    if request.method == 'POST':
        identity = request.form.get('studnbr')
        # We needed and used to connect to the admin panel, this feature should be replaced with another, better way.
        # For demonstration purpose, this works.
        if int(identity) == 7061:
            return redirect(url_for('admin_login_function'))
        if check_if_identity_exists(int(identity)) is True:
            return identity
            # return redirect(url_for('fixing', identity=identity, order=order))
        else:
            flash('That number does not exist in our database or already has a card, please register a new account.'
                  '  If you think this is an error, contact the faculty.')
            return redirect(url_for('studid_fix_card', order=order))

    else:
        return render_template('studid.html')


@app.route('/dont/worry/im/working/on/it/<identity>/<order>')
def fixing(identity, order):
    return render_template('card_fixer.html', type=order, aids=identity)


@app.route('/do_the_fixing/<int:order>/<int:aid>', methods=['GET', 'POST'])
def do_the_fixing(order, aid):
    if request.method == 'POST':
        card = read()
        while card is None:
            pass

        if card is False:
            flash('You did not scan your card in time.')
            return Response("fail", status=408, mimetype='application/json')

        # makes sure the card doesn't already exist in our database.
        if card_exists_already(card[0]) is True:
            flash('This card already exists in our database')
            return Response('fail', status=409, mimetype='application/json')

        if order is 1:
            add_student_card_with_studid(card[0], aid)
        elif order is 2:
            add_student_card(aid, card[0])
        else:
            flash('Something went wrong')
            return Response("fail", status=406, mimetype='application/json')
        flash('Your card was added successfully!')
        return Response("done", status=200, mimetype='application/json')
    else:
        return redirect(url_for('splash'))


# ########################################################### #
# #                  ONLY FOR OBS STUDIO!                   # #
# ########################################################### #

def obs_status_change(room_id, command):
    room = get_room_info(room_id)
    ip = room[3]
    firewall = int(room[4])
    password = str(room[5])
    obs_connector(ip, firewall, password, command)
    return True


# ########################################################### #
# #                    Admin panel!                         # #
# ########################################################### #

@app.route("/admin")
def admin_main():
    ax = count_all_completed_exams()
    l30d = count_all_last_30_days()
    l24d = count_last_24_hours()
    passed = count_passed_exams()

    # Adds all data into a single list before being sent to the index page.
    website_strings = [ax[0], l30d[0], l24d[0], passed[0]]

    all_last30days = last_30_day_count_per_day()

    return render_template('admin/index.html', ws=website_strings, last30days=all_last30days)


@app.route("/tablet-config", methods=['GET', 'POST'])
def tablet_config():
    if request.method == 'POST':
        r = request.form.get('roomNbR')
        session['room'] = r
        update_room(r, str(session.get('tablet_token')))
        flash('Aktiv Rom nummer er lagret!', 'success')

        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=365)

        return redirect(url_for('tablet_config'))
    else:
        room_list = obs_rooms_available()
        return render_template('admin/tablet-control.html', rooms=room_list)


@app.route("/obs", methods=['GET', 'POST'])
def obs_room_control():
    installed_rooms = obs_rooms_available()
    return render_template('admin/obs-control.html', rdy=installed_rooms)


@app.route("/obs/delete/<room_id>", methods=['POST'])
def obs_delete_room(room_id):
    if request.method == 'POST':
        delete_obs_room_db(room_id)
        return Response("done", status=200, mimetype='application/json')
    else:
        return Response("fail", status=406, mimetype='application/json')


@app.route("/obs/add", methods=['POST'])
def obs_add_new_room():
    if request.method == 'POST':
        name = request.form.get('validationName')
        number = 0

        ip = request.form.get('validationIP')
        wall = request.form.get('validationWall')
        pw = request.form.get('validationPassword')
        add_new_room_to_db(name, number, ip, wall, pw)

        flash('Rom er lagt til.', 'success')
        return redirect(url_for('obs_room_control'))
    else:
        return redirect(url_for('obs_room_control'))


@app.route("/obs_adding", methods=['POST'])
def obs_add_new_room_t():
    if request.method == 'POST':
        data = request.get_json()

        i = data['id']
        nm = data['name']
        ip = data['ip']
        fwall = data['firewall']
        passw = data['password']

        update_obs_room_info(i, nm, ip, fwall, passw)
        flash('Rom informasjon endret', 'success')

        return Response("success", status=200, mimetype='application/json')
    else:
        return None


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


@app.route("/admin/exams/new/post")
def admin_exams_new_post():
    return redirect(url_for('admin_exams'))


@app.route("/admin/exam/<ex_id>", methods=['GET', 'POST'])
def admin_exam_edit(ex_id=None):
    if request.method == 'POST':
        data = request.form

        # Exam Info

        name = data['shortname']
        outfit = data['outfit']
        mincorr = data['min_correct']
        time = "00:" + data['max_time'] + ":00"
        desc = ""

        description = find_replace_keys(data, "testdescription_")

        # Puts the description fields into a string for easier storage.
        for d in description:
            if description[d]:
                desc += str(description[d])
                desc += "|"
        desc = desc[:-1]  # This removes the last | from the string.

        if ex_id == "0":
            update_exam_info(name, desc, outfit, time, mincorr, ex_id)

            # Questions

            questions = find_replace_keys(data, "q_")
            for e in questions:
                update_questions_if_edited(str(e), questions[e])

            # finds and replaces anything that starts with the text "important_"
            res = find_replace_keys(data, "important_")
            # updates every question with the correct important status.
            for e in res:
                update_important_questions(str(e), res[e])

            exam_identity = ex_id
        else:
            exam_identity = admin_add_new_exam(name, desc, outfit, time, mincorr)
            flash_msg = f'Eksamen med navn: "{name}" er lagret'
            flash(flash_msg, 'success')

        # finds all that has the text "new_" in them
        new_quest = find_replace_keys(data, "new_")
        new_quest_imp = find_replace_keys(data, "i_ne_")

        # if there are new questions, adds them to the database
        if new_quest is not None:
            for x in new_quest:
                if new_quest[x]:
                    add_new_questions(ex_id, new_quest[x], new_quest_imp[x])
        return redirect(url_for('admin_exam_edit', ex_id=exam_identity))
        # return desc

    if ex_id != "0":
        exam = admin_get_exam_info(ex_id)
        splitter = exam[3].split('|')
        time = exam[5][3:-3]

        questions = exam_get_questions(ex_id)
        return render_template('admin/edit_exam.html', exam=exam, info=splitter,
                               questions=questions, time=time)
    else:
        return render_template('admin/view-exam.html')


@app.route("/question/delete/<qid>", methods=['POST'])
def admin_delete_question(qid):
    if request.method == 'POST':
        db_delete_question(qid)
        return Response("done", status=200, mimetype='application/json')
    else:
        return Response("fail", status=406, mimetype='application/json')


# Sensors
@app.route("/admin/users")
def admin_users():
    usr = all_student_users()
    tch = all_teacher_users()
    return render_template('admin/users.html', usr=usr, tch=tch)


@app.route("/admin/view/user/<id>")
def admin_view_user(id):
    u = get_user_info(id)
    if u is False:
        return None

    return None


@app.route("/admin/users/new", methods=['GET', 'POST'])
def admin_new_users():
    if request.method == 'POST':
        data = request.form
        fname = data['fname']
        lname = data['lname']
        utype = data['usertype']
        email = data['mail']

        pw = 0
        studid = 0

        if int(utype) is 1:
            studid = data['studid']

        if int(utype) is 3:
            pw = data['pass']

        register_new_user(fname, lname, utype, email, pw, studid)
        return redirect(url_for('admin_users'))

    utype = get_user_types()
    return render_template('admin/new_user.html', utype=utype)


@app.route("/admin/users/edit/<uid>", methods=['GET', 'POST'])
def admin_user_edit(uid):
    if request.method == 'POST':
        data = request.form

        fname = data['fname']
        lname = data['lname']
        utype = data['usertype']
        email = data['mail']

        pw = 0
        studid = 0

        if int(utype) is 1:
            studid = data['studid']

        if int(utype) is 3:
            pw = data['pass']

        admin_update_user(uid, fname, lname, utype, email, pw, studid)

        return redirect(url_for('admin_users'))
    else:
        utype = get_user_types()
        eu = edit_user(uid)
        return render_template('admin/edit_user.html', utype=utype, u=eu)


@app.route("/admin/users/<int:eid>/<int:funct>", methods=['GET'])
def admin_users_switch(eid, funct):
    error = None
    if funct == 1:
        activate_user(eid)
        flash(f'You successfully activated the user with id: {eid}', 'success')
        return redirect(url_for('admin_exams'))
    elif funct == 0:
        deactivate_user(eid)
        flash(f'You successfully deactivated a user with id: {eid}', 'success')
        return redirect(url_for('admin_exams'))
    else:
        flash(f'Server error, do not worry. Please try again.', 'error')
        return redirect(url_for('admin_exams'))


@app.route("/admin/results")
def admin_responses():
    r = get_all_results()
    time_list = []
    for x in r:
        new_time = convert_time(x[3])
        new_time = new_time.strftime("%M min og %S sekunder")
        time_list.append(new_time)

    l = zip(r, time_list)
    return render_template('admin/answers.html', results=l)


@app.route("/admin/results/view/<rid>")
def admin_responses_single(rid):
    result = get_single_result(rid)
    answers = result[4].split('|')

    exam_info = get_exam_info(result[3])
    info_to_student = exam_info[3].split('|')

    questions = exam_get_questions(result[3])

    conv_dated = convert_date(result[2])
    dated = conv_dated.strftime("%d %b, %Y")

    time_used = result[7].split('.')

    if result[5] is not '0':
        sensor = get_sensor_from_card(result[5])
    else:
        sensor = None

    # This makes sure the database entry has the correct format, makes it more secure.
    # If it doesn't have the correct format, it sends empty strings to the webpage.
    if is_json(result[10]):
        comments = json.loads(result[10])
    else:
        comments = {'good': '', 'bad': '', 'other': ''}

    # Zips the two variable together so they can be used more effectively on the page.
    zipped = zip(questions, answers)

    return render_template('admin/view-answers.html', r=result, exam_info=info_to_student, p=zipped, comment=comments,
                           date=dated, tu=time_used[0], sensor=sensor)


@app.route('/remove/card/from/<user>', methods=['POST'])
def admin_remove_card(user):
    if request.method == 'POST':
        admin_remove_card_from_user(user)
        return Response("done", status=200, mimetype='application/json')
    else:
        return redirect(url_for('admin_main'))


@app.route('/logintoadmin', methods=['GET', 'POST'])
def admin_login_function():
    if request.method == 'POST':
        password = request.form.get('admin')
        admin_check_checking = check_password_against_main_admin(password)
        if admin_check_checking is True:
            return redirect(url_for('admin_main'))
        else:
            return redirect(url_for('splash'))
    else:
        return render_template('admin/signin.html')


# ########################################################### #
# #                         Login                           # #
# ########################################################### #

@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    # This function is not yet ready for use.
    # Needs more work before implementing this.
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

def find_replace_keys(data, p):
    r = {key: val for key, val in data.items()
         if key.startswith(p)}
    # removes the text "specified in p", for easier querying.
    r = {x.replace(p, ''): v
         for x, v in r.items()}
    return r


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


def convert_time(time):
    if '.' in time:
        format = '%H:%M:%S.%f'
    else:
        format = '%H:%M:%S'
    datetime_str = datetime.strptime(time, format)
    return datetime_str


def convert_date(date_time):
    format = '%Y-%m-%d'  # The format
    datetime_str = datetime.strptime(date_time, format)

    return datetime_str


def is_json(string):
    try:
        json_object = json.loads(string)
    except ValueError as e:
        return False
    return True


# ########################################################### #
# #                     Full app reset!                     # #
# ########################################################### #
@app.route('/hidden/delete/function/that/is/hidden/<xid>')
def hidden_delete_function_that_is_hidden(xid):
    # Special function for actually deleting exams, should only be used for testing purpose.
    if for_testing_purpose is True:
        hidden_delete_function(xid)
        x = f'Exam with id: {xid} has been deleted!'
        return x
    else:
        redirect(url_for('splash'))


# @app.route('/install', methods=['GET'])
def first_time_install():
    # This function is not available
    if session.get('tablet_unique_id') is None:
        unique = uuid.uuid1()
        session['tablet_unique_id'] = unique
        add_to_active_tablets(unique)
    return redirect(url_for('splash'))


# @app.route('/reset', methods=['GET'])
def reset_tablet():
    session_reset()
    if session.get('tablet_unique_id'):
        delete_from_active_tablets(session.get('tablet_unique_id'))
        session.pop('tablet_unique_id', None)
    return redirect(url_for('first_time_install'))


def session_reset():
    """
    Reset of all non-essential websites sessions.
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
    """Page not found."""
    return make_response(render_template("404.html"), 404)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


# Starts the app on local network.
if __name__ == '__main__':
    app.run(host='0.0.0.0')
