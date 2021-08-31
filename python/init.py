from colorama import init
import pandas as pd
import pickle
import math
# import yaml
import os


init()  # init colors in terminal
version = '0.1.0'
os.chdir(f'{__file__}/../..')  # project root folder
project_name = 'gmanka_backup'
pd.set_option('mode.chained_assignment', None)


# def save(df):
#     df.to_csv(f'data/{df.name[0]}.csv', index=False)
#     # this function crated to fuck buggy pycharm warning
#     # https://stackoverflow.com/questions/68787744


class Telegram:
    phone_number = None
    api_hash = None
    api_id = None


def dump(data, name: str):
    pickle.dump(data, open(f'data/pickle/{name}', 'wb'))


def load(name: str):
    return pickle.load(open(f'data/pickle/{name}', 'rb'))


if 'data' not in os.listdir():
    os.mkdir('data')


if 'telegram' not in os.listdir('data/pickle'):
    # telegram = {
    #     'phone_number': None,
    #     'api_hash': None,
    #     'api_id': None,
    # }
    telegram = Telegram
    dump(telegram, 'telegram')

telegram = load('telegram')


def nice(size_bytes):
    if size_bytes == 0:
        return "0B"
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, index)
    converted_size = round(size_bytes / p, 2)
    return f'{converted_size} {units[index]}'
