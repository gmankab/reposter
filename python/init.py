from colorama import init
import pandas as pd
import math
import os


init()  # init colors in terminal
version = '0.1.0'
os.chdir(f'{__file__}/../..')  # project root folder
project_name = 'gmanka_backup'
pd.set_option('mode.chained_assignment', None)


def save(df):
    df.to_csv(f'data/{df.name[0]}.csv', index=False)
    # this function crated to fuck buggy pycharm warning
    # https://stackoverflow.com/questions/68787744


if 'data' not in os.listdir():
    os.mkdir(project_name)

if 'pickle' not in os.listdir('data'):
    os.mkdir('data/pickle')

if 'telegram.csv' not in os.listdir('data'):
    save(pd.DataFrame({
        'name': 'telegram',
        'phone_number': None,
        'api_hash': None,
        'api_id': None,
    }, index=[0]))


telegram = pd.read_csv('data/telegram.csv')


def nice(size_bytes):
    if size_bytes == 0:
        return "0B"
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    converted_size = round(size_bytes / p, 2)
    return f'{converted_size} {units[i]}'
