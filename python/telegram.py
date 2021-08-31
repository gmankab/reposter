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
import time


class ManyRequestsError(Exception):
    pass


class JsonDecodeError(Exception):
    pass


async def input_phone(session, user_agent):
    form_data = {'phone': telegram.phone_number[0]}
    answer = await session.post(
        'https://my.telegram.org/auth/send_password',
        data=form_data, headers=user_agent)

    try:
        random_hash = answer.json()['random_hash']
        return random_hash

    except json.decoder.JSONDecodeError:
        if answer.text == 'Sorry, too many tries. Please try again later.':
            raise ManyRequestsError(
                'too many requests to telegram servers\n'
                'try to change your ip or input another phone number\n'
                'or phone number is wrong, make sure it registered in telegram')
        else:
            raise ("can't decode json from:\n\n" + answer.text)


async def input_code(session, user_agent, random_hash, code):
    form_data = {
        'phone': telegram.phone_number[0],
        'random_hash': random_hash,
        'password': code,
        'remember': 1,
    }

    answer = await session.post(
        'https://my.telegram.org/auth/login',
        data=form_data, headers=user_agent)

    if answer.text == 'true':
        await create_app(session, user_agent)
    else:
        cprint(f'Error in line 69:\n{answer.text}', 'red')


async def create_app(session, user_agent):
    answer = await session.get('https://my.telegram.org/apps', headers=user_agent)
    my_hash = Bs(answer.content, 'html.parser').select('input[name="hash"]')[0]['value']

    form_data = {
        'hash': my_hash,
        'app_title': 'aboba',
        'app_shortname': 'aboba',
        'app_platform': 'desktop',
        'app_url': '',
        'app_desc': '',
    }

    answer = await session.post(
        'https://my.telegram.org/apps/create',
        data=form_data, headers=user_agent)

    print(answer.text)


async def get_data2(session, user_agent):
    answer = await session.get('https://my.telegram.org/apps', headers=user_agent)
    print(Bs(answer.text, features='html.parser'))
    return 'successfully logged in telegram'


async def upload_telegram():
    client = TelegramClient(project_name, telegram['api_id'], telegram['api_hash'])
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


def dump(data, name):
    pickle.dump(data, open(f'data/pickle/{name}', 'wb'))


def load(name):
    return pickle.load(open(f'data/pickle/{name}', 'rb'))


async def main():
    # parsing https://my.telegram.org
    session = requests.session()
    user_agent = {'User-Agent': UserAgent().random}

    # session, user_agent =

    print(session)
    print(user_agent)

    telegram.phone_number[0] = ''
    random_hash = await input_phone(session, user_agent)

    code = input(
        'Now input code from telegram pm\n'
        'it should be something like B4n_h6Mdg-9:\n'
    )

    await input_code(session, user_agent, random_hash, code)


# main()
