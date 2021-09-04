# python 3.10 +
from dataclasses import dataclass
import pickle
import yaml
import os


def init(path=os.getcwd()):
    os.chdir(path)
    if 'data' not in os.listdir():
        os.mkdir('data')


class NameExpectedError(Exception):
    @staticmethod
    def text(data):
        if isinstance(data, dict):
            name = 'dict'
        else:
            name = 'else'
        return open(f'error_messages/{name}.txt').read()


def dump(data, name: str = None):
    if not name:
        if isinstance(data, dict):
            if 'name' not in data.keys():
                raise NameExpectedError(NameExpectedError.text(data))
            name = data['name']
        else:
            if 'name' not in vars(data).keys():
                raise NameExpectedError(NameExpectedError.text(data))
            name = data.name
    extension = name.split('.')[-1]
    match extension:
        case 'pickle':
            pickle.dump(data, open(f'data/{name}', 'wb'))
        case 'yml':
            if type(data) is not dict:
                data = data.to_dict
            yaml.dump(data, open(f'data/{name}', 'w'))


def load(name: str):
    extension = name.split('.')[-1]
    match extension:
        case 'pickle':
            return pickle.load(open(f'data/{name}', 'rb'))
        case 'yml':
            return yaml.safe_load(open(f'data/{name}', 'r'))


class BetterData:
    """
    @DynamicAttrs
    disabling pycharm "unresolved attribute" warnings
    """
    def __init__(self, data: dict, name: str = None):
        if name:
            data['name'] = name
        for key, val in data.items():
            vars(self)[key] = val

    def to_dict(self, name=False):
        return vars(self)
