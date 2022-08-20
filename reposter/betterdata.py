#!/bin/python

'''
BETTERDATA
https://github.com/gmankab/betterdata
'''

from rich import (
    pretty,
    traceback,
)
import rich
from pathlib import Path
import gmanka_yml as yml
from collections.abc import Iterable


pretty.install()
traceback.install(
    show_locals=True
)
c = rich.console.Console()
print = c.print
version = '22.1.0'


class Data:
    '''
    @DynamicAttrs
    '''
    def __init__(
        self,
        data: dict = {},
        file_path: str | Path = None,
    ) -> None:
        self.data = {}
        self.file_path = None
        self.set_data(
            data = data,
            file_path = file_path,
        )
        if (
            not self.data
        ) and (
            self.file_path
        ) and (
            self.file_path.exists()
        ):
            self.read_file()

    def __repr__(self) -> any:
        return self.data

    def __getitem__(
        self,
        item,
    ) -> any:
        return self.data[item]

    def __setitem__(
        self,
        key,
        val,
    ) -> None:
        self.data[key] = val
        vars(self)[key] = val

    def __add__(
        self,
        additional,
    ):
        return self.data + additional

    def set_data(
        self,
        data: dict = {},
        file_path = None
    ):
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                f'expected [green]dict but {type(data)} got'
            )

        if file_path:
            self.file_path = Path(file_path)
        if data:
            self.data = data
            for key, val in data.items():
                vars(self)[key] = val

    def to_str(
        self
    ):
        return yml.to_str(
            data = self.data
        )

    def read_file(
        self,
        file_path = None,
    ):
        self.set_data(
            file_path = file_path,
        )
        self.set_data(
            data = yml.read_file(
                file_path = self.file_path
            )
        )

    def to_file(
        self,
        file_path = None
    ):
        self.set_data(
            file_path = file_path
        )
        yml.to_file(
            data = self.data,
            file_path = self.file_path,
        )

    def print(
        self
    ):
        c.print(
            self.data
        )


data2 = Data(
    {
        'a': 1,
        2: 'b',
    }
)
