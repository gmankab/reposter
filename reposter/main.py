#!/bin/python
from setup import (
    app_version,
    app_name,
    proj_path,
    yes_or_no,
)
from rich import (
    pretty,
    traceback,
)
from betterdata import Data
import rich
from pathlib import Path
from easyselect import Selection
from dataclasses import dataclass
import subprocess
import gmanka_yml as yml
import pyrogram

pretty.install()
traceback.install(
    show_locals=True
)
c = rich.console.Console()
print = c.print
config_path = Path(
    f'{proj_path}/config.yml'
)
run_st = subprocess.getstatusoutput


def config_create():
    if config_path.exists():
        Data.config = yml.read_file(
            config_path
        )
    else:
        # Data.api_id: interact_input('api_id')
        #     'api_hash:
        # Data.config = {

        # }

        pass


def run(
    command: str
) -> str:
    return run_st(
        command
    )[-1]


def interact_input(
    item: str
):
    while True:
        print(f'\nplease input {item}')
        val = input()
        if not val:
            continue
        print(
            f'[deep_sky_blue1]{item}[/deep_sky_blue1] - is it correct?'
        )
        if yes_or_no.choose() == 'no':
            continue
        return val


# bot = pyrogram.client.Client(
#     api_id = Data.api_id,
#     api_hash = Data.api_hash,
#     name = 'reposter',
#     # app_version = f'reposter {version}',
# )
