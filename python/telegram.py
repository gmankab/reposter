import time

from init import *
from termcolor import colored, cprint
from fake_useragent import UserAgent
from telethon import TelegramClient
from bs4 import BeautifulSoup as Bs
from dataclasses import dataclass
import urllib.request as r
import requests
import pickle
import json

pd.set_option('mode.chained_assignment', None)


def start():
    # parsing https://my.telegram.org
    session = requests.session()
    user_agent = {'User-Agent': UserAgent().random}

    telegram.phone_number[0] = '+7 800 555 35 35'

    form_data = {'phone': telegram.phone_number[0]}
    answer = session.post(
        'https://my.telegram.org/auth/send_password',
        data=form_data, headers=user_agent)

    try:
        telegram.random_hash[0] = answer.json()['random_hash']

        session_file = open('data/cookies.txt', 'wb')
        pickle.dump(session, session_file)

        save(telegram)
        # time.sleep(1)
        input_code(session, user_agent)
    except json.decoder.JSONDecodeError:
        if answer.text == 'Sorry, too many tries. Please try again later.':
            cprint('to many requests to telegram servers\n'
                   'try to change your ip or input another phone number\n'
                   'or phone number is wrong, make sure it registered in telegram, ', 'red')
        else:
            cprint(f'Error:\n{answer.text}', 'red')


def input_code(session, user_agent):
    session_file = open('data/cookies.txt', 'wb')
    pickle.dump([session, user_agent], session_file)

    form_data = {
        'phone': telegram.phone_number[0],
        'random_hash': telegram.random_hash[0],
        'password': input('Now input code from telegram pm\n'
                          'It should be something like B4n_h6Mdg-9: '),
        'remember': 1,
    }

    answer = session.post(
        'https://my.telegram.org/auth/login',
        data=form_data, headers=user_agent)

    if answer.text == 'true':
        create_app(session, user_agent)
    else:
        cprint(f'Error:\n{answer.text}', 'red')


def create_app(session, user_agent):
    session_file = open('data/cookies.txt', 'wb')
    pickle.dump([session, user_agent], session_file)

    answer = session.get('https://my.telegram.org/apps', headers=user_agent)
    print(answer.json())

    form_data = {
        'hash': '8cab5b23e32958c2dc',
        'app_title': 'test',
        'app_shortname': 'test',
        'app_platform': 'desktop',
        # 'app_url': '',
        # 'app_desc': '',
    }

    # answer = session.post('https://my.telegram.org/apps',
    #                       data=form_data, headers=user_agent)


def get_api_id_n_hash(session, user_agent):
    session_file = open('data/cookies.txt', 'wb')
    pickle.dump([session, user_agent], session_file)

    answer = session.get('https://my.telegram.org/apps', headers=user_agent)

    print(Bs(answer.text, features='html.parser'))
    print('successfully logged in telegram')


async def upload_telegram():
    client = TelegramClient(name, telegram['api_id'], telegram['api_hash'])
    await client.connect()

    # if not await client.is_user_authorized():
    #     await client.send_code_request(telegram['account_phone_number'])
    #     await client.sign_in(telegram['account_phone_number'], input('Enter code: '))


async def send_file(client):
    chat = await client.get_input_entity(telegram['phone_number'])

    def progress_callback(current, total):
        print(f'{round(current / total * 100, 1)}% Uploaded {nice(current)} out of {nice(total)}')

    await client.send_file(
        entity=chat,
        file="C:/Users/Gmank/Desktop/srv2.zip",
        caption="aboba",
        progress_callback=progress_callback
    )

start()
# get_api_id_n_hash(*pickle.load(open('data/cookies.txt', 'rb')))
# create_app()
