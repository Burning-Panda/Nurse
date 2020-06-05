from flask import session
import json


#  Language option.


#    Edit this to change lang,
#    this option is here in case we want international students to use our product.
# set_lang('no')

lang_en = '{ "no_card_in_db": "This card doesn\'t exists in our database, please register as a new user",' \
          '"no_card_scan_timed": "You did not scan your card in time.",' \
          '"": "", ' \
          '"": "", ' \
          '}'
lang_no = '{"no_card_in_db": "Dette kortet finnes ikke i vår database. Registrer deg som ny bruker",' \
          '"no_card_scan_timed": "Du skannet ikke kortet ditt i tide.", ' \
          '"": "", ' \
          '"": "", ' \
          '"grade_p":"Bestått"}'

lang = None


def set_lang(l):
    session['lang'] = l

    if session['lang'] == 'en':
        lang = json.loads(lang_en)
    elif session['lang'] == 'no':
        lang = json.loads(lang_no)