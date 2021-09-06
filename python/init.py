# python 3.10 +
from colorama import init as colorama_init
from get_telegram import telegram
from dataclasses import dataclass
import betterdata as bd
import math
import os


@dataclass()
class Project:
    version = '0.1.0'
    root_folder = os.path.realpath(f'{__file__}/../..')
    name = 'gmanka_backup'


colorama_init()


# pd.set_option('mode.chained_assignment', None)
# def save(df):
#     df.to_csv(f'data/{df.name[0]}.csv', index=False)
#     # this function crated to fuck buggy pycharm warning
#     # https://stackoverflow.com/questions/68787744


def nice(size_bytes):
    if size_bytes == 0:
        return "0B"
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(size_bytes, 1024)))
    return f'{round(size_bytes / math.pow(1024, index), 2)} {units[index]}'
