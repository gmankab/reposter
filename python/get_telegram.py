# python 3.10 +
from init import *
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as Bs
import betterdata as bd
import requests
import json


def input_phone(session, user_agent):
    class TooManyRequestsError(Exception):
        pass

    form_data = {'phone': telegram.phone_number}
    answer = session.post(
        'https://my.telegram.org/auth/send_password',
        data=form_data, headers=user_agent)

    try:
        random_hash = answer.json()['random_hash']
        return random_hash

    except json.decoder.JSONDecodeError:
        if answer.text == 'Sorry, too many tries. Please try again later.':
            raise TooManyRequestsError(
                'too many requests to telegram servers\n'
                'try to change your ip or input another phone number\n'
                'or phone number is wrong, make sure it registered in telegram')
        else:
            raise "can't decode json from:\n\n" + answer.text


def input_code(session, user_agent, random_hash, code):
    form_data = {
        'phone': telegram.phone_number,
        'random_hash': random_hash,
        'password': code,
        'remember': 1,
    }

    answer = session.post(
        'https://my.telegram.org/auth/login',
        data=form_data, headers=user_agent)

    if answer.text != 'true':
        class InputCodeError(Exception):
            pass
        raise InputCodeError(f'Error in line 69:\n{answer.text}', 'red')


def create_app(session, user_agent):
    answer = session.get('https://my.telegram.org/apps', headers=user_agent)
    my_hash = Bs(answer.content, 'html.parser').select('input[name="hash"]')[0]['value']

    form_data = {
        'hash': my_hash,
        'app_title': 'aboba2',
        'app_shortname': 'aboba2',
        'app_platform': 'desktop',
        'app_url': '',
        'app_desc': '',
    }

    session.post(
        'https://my.telegram.org/apps/create',
        data=form_data, headers=user_agent)


def get_webpage(session, user_agent):
    return session.get('https://my.telegram.org/apps', headers=user_agent).content


def get_api_id(webpage):
    return str(list(list(Bs(webpage, 'html.parser').select(
        'span[class="form-control input-xlarge uneditable-input"]')[0])[0])[0])


def get_api_hash(webpage):
    return str(list(Bs(webpage, 'html.parser').select(
        'span[class="form-control input-xlarge uneditable-input"]')[1])[0])


def get_telegram():
    # parsing https://my.telegram.org
    session = requests.session()
    session.name = 'session.pickle'
    user_agent = {
        'User-Agent': UserAgent().random,
        'name': 'user_agent.yml',
    }

    telegram.phone_number = input(
        'please input your phone number,\n'
        'so that we can make a bot and send world saves to telegram:\n'
    )
    bd.dump(telegram)

    random_hash = input_phone(session, user_agent)
    code = input(
        'Now input code from telegram pm,\n'
        'it should be something like B4n_h6Mdg-9:\n'
    )
    input_code(session, user_agent, random_hash, code)

    bd.dump(session)
    bd.dump(user_agent)

    create_app(session, user_agent)
    webpage = get_webpage(session, user_agent)

    bd.dump(session)
    bd.dump(user_agent)

    telegram.api_id = get_api_id(webpage)
    telegram.api_hash = get_api_hash(webpage)

    bd.dump(telegram)

    return telegram
