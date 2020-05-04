from flask import session
import json


#  Language option.


#    Edit this to change lang,
#    this option is here in case we want international students to use our product.
# set_lang('no')

lang_en = '{ "no_user":"No such user",' \
          '"no_exam":"Sorry, that exam is not active or doesn\'t exists",' \
          '"":""}'
lang_no = '{"no_user":"Finner ingen bruker",' \
          '"no_exam":"Den eksamen er ikke aktiv eller finnes ikke",' \
          '"grade_f":"Ikke bestått"' \
          '"grade_p":"Bestått"}'

lang = None


def set_lang(l):
    session['lang'] = l

    if session['lang'] == 'en':
        lang = json.loads(lang_en)
    elif session['lang'] == 'no':
        lang = json.loads(lang_no)