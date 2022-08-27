#!/bin/python

'''
BETTERDATA
https://github.com/gmankab/betterdata
'''

from easyselect import Selection
from pathlib import Path
import gmanka_yml as yml
from rich import (
    pretty,
    traceback,
)
import rich
import sys


yes_or_no = Selection(
    items = [
        'yes',
        'no',
        'cancel'
    ],
    styles = [
        'green',
        'red',
        'bright_black'
    ]
)


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

    def __repr__(self) -> dict:
        return self.data

    def __str__(self) -> str:
        return str(self.data)

    def __getitem__(
        self,
        item,
    ) -> any:
        if item in self.data:
            return self.data[item]
        else:
            return None

    def __setitem__(
        self,
        key,
        val,
    ) -> None:
        self.data[key] = val
        vars(self)[key] = val
        self.to_file()

    def __add__(
        self,
        additional,
    ) -> dict:
        return self.data + additional

    def __contains__(
        self,
        item,
    ) -> bool:
        return item in self.data

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
            self.to_file()

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
        if self.file_path and self.data:
            yml.to_file(
                data = self.data,
                file_path = self.file_path,
            )

    def interact_input(
        self,
        item: str,
        try_int: bool = True,
        stop_if_exist: bool = True,
        exit_on_cancel: bool = True,
        selection: Selection = yes_or_no,
    ):
        if stop_if_exist and self[item]:
            return

        while True:
            print(f'\n[bold]input {item}:')
            val = input()
            if not val:
                continue
            print(
                f'[deep_sky_blue1]{val}[/deep_sky_blue1] - is it correct?'
            )

            match selection.choose():
                case 'no':
                    continue
                case 'cancel':
                    if exit_on_cancel:
                        sys.exit()
                    else:
                        return
                case 'yes':
                    if try_int and val.isdigit():
                        val = int(val)
                    self[item] = val
                    if self.file_path:
                        self.to_file()
                        print(f'[green]{item} saved to config:\n[deep_sky_blue1]{self.file_path}')
                    return

    def print(
        self
    ):
        c.print(
            self.data
        )
