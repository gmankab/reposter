#!/bin/python
from setup import (
    app_version,
    app_name,
    proj_path,
    portable,
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
import platform
import os

pretty.install()
traceback.install(
    show_locals=True
)
c = rich.console.Console()
print = c.print
run_st = subprocess.getstatusoutput
config = Data(
    file_path=Path(
        f'{proj_path}/config.yml'
    )
)

os_name = platform.system()
if os_name == 'Linux':
    os_name = platform.freedesktop_os_release()['PRETTY_NAME']
os_name = f'{os_name} {platform.release()}'
python_imp = f'{platform.python_implementation()} {platform.python_version()}'

app_full_name = f'''
gmanka {app_name} {app_version},
pyrogram {pyrogram.__version__},
{python_imp}\
'''

if portable:
    app_full_name = f'portable {app_full_name}'

print(
    app_full_name,
    os_name,
    sep = ',\n',
    highlight = False,
)

bot: pyrogram.client.Client = None


def chat(
    chat_id: str | int
) -> pyrogram.types.Chat:
    return bot.get_chat(chat_id)


def parse_link(
    chat_link: str
):
    chat_link = chat_link.replace(
        'https://',
        '',
    ).replace(
        'http://',
        '',
    )
    id = None
    if chat_link[:6] == 't.me/+':
        pass
    elif chat_link[:4] == 't.me':
        chat_link = chat_link.replace(
            't.me/',
            '@',
        )
    elif chat_link[0] == '@':
        pass
    elif (
        'webz.telegram.org/#' in chat_link
    ) or (
        'web.telegram.org/z/#' in chat_link
    ):
        id = int(
            chat_link.rsplit(
                '#',
                1
            )[-1]
        )
        print(f'id = {id}')
    else:
        return f'"{chat_link}" is not a telegram link'

    try:
        if id:
            chat(id)
        else:
            chat(chat_link)
        return f'{chat_link} - valid link\n\nsaved to config'
    except Exception as exception:
        c.print_exception(
            show_locals=True
        )
        return f'{chat_link} - invalid link\n\n{exception}'


def run(
    command: str
) -> str:
    return run_st(
        command
    )[-1]


def init_config() -> None:
    for item in (
        'api_id',
        'api_hash',
    ):
        if item not in config:
            print('\nPlease open https://my.telegram.org/apps and get api_id and api_hash')
            print(
'''\
[bold red]WARNING:[/bold red] [bold white]use ony your own api_id and api_hash.[/bold white] I already tried to take them from decompiled official telegram app, and 20 minutes later my telegram account get banned. Then I wrote email with explanation on recover@telegram.org and on the next day and they unbanned me.
''', highlight = False
            )
            break
    for item in (
        'api_id',
        'api_hash',
        'phone_number',
    ):
        config.interact_input(item)
    if 'chats_tree' not in config:
        config['chats_tree'] = {}


def main() -> None:
    init_config()
    global bot
    if 'session' in config and config.session:
        bot = pyrogram.client.Client(
            name = app_name,
            session_string = config.session,
        )
        first_start = False
    else:
        phone_number = str(config.phone_number)
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        bot = pyrogram.client.Client(
            name = app_name,
            api_id = config.api_id,
            api_hash = config.api_hash,
            phone_number = phone_number,
            app_version = app_full_name,
            device_model = os.getlogin(),
            system_version = os_name,
            in_memory = True,
            workers = 1,
        )
        first_start = True

    with bot:
        if first_start:
            config['session'] = bot.export_session_string()
        if 'logs_chat' not in config:
            bot.send_message(
                chat_id = chat("me").id,
                text = '''\
Please create new empty chat and send here clickable link to it. You will use it to configure script. You must be admin, and nobody except you must have access to this chat

acceptable formats:
@username
t.me/chat_name
t.me/+6XqO65TrfatjNGU6
webz.telegram.org/#-1657778608
'''
            )
        # for link in [
        #     'https://t.me/gmanka',
        #     # 't.me/sdasldkasldkas',
        #     't.me/+6XqO65TrfatjNGU6',
        #     'https://webz.telegram.org/#-1657778608'
        # ]:
        #     print(parse_link(link))
        # print(f'\n[bold green]please open telegram webz and see your "saved messages" chat in telegram - [/bold green][bold]{self_chat}')
        print(chat('t.me/+6XqO65TrfatjNGU6'))


main()
