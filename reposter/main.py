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
from pathlib import Path
from betterdata import Data
from easyselect import Selection
from dataclasses import dataclass
from pyrogram.handlers import MessageHandler
import gmanka_yml as yml
import subprocess
import pyrogram
import platform
import asyncio
import rich
import time
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

start_message = f'{app_full_name},\n{os_name}'


print(
    start_message,
    highlight = False,
)

bot: pyrogram.client.Client = None
self_chat_handler = None


def chat(
    chat_id: str | int
) -> pyrogram.types.Chat:
    return bot.get_chat(chat_id)


def check_chat_exist(chat_id):
    try:
        chat(chat_id)
        return True
    except Exception as exception:
        return exception


def is_group(
    chat_id,
    chat_link,
):
    if chat(chat_id).type in [
        pyrogram.enums.ChatType.GROUP,
        pyrogram.enums.ChatType.SUPERGROUP,
    ]:
        try:
            bot.get_chat_member(
                chat_id, "me"
            )
        except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
            return f'you are not a member of {chat_link}'
            
        return f'successfully set {chat_link} as chat for settings and logs, please open it'
    else:
        return f'{chat_link} is not a group chat'


def get_id():
    pass


def init_parse_link(
    chat_link: str
):
    chat_link = chat_link.replace(
        'https://',
        '',
    ).replace(
        'http://',
        '',
    )
    chat_id = None
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
        chat_id = chat_link.rsplit(
            '#',
            1,
        )[-1]
        # print(f'id = {id}')
        if check_chat_exist(
            int(chat_id)
        ) is True:
            return is_group(int(chat_id), chat_link)
        else:
            chat_id = int(
                chat_id.replace(
                    '-',
                    '-100',
                )
            )
            if check_chat_exist(
                chat_id,
            ) is True:
                return is_group(chat_id, chat_link)
            else:
                return f'{chat_link} is a bad link'
    else:
        return f'{chat_link} is not working telegram link'
    if check_chat_exist(
        chat_link
    ) is True:
        return is_group(chat_link, chat_link)
    else:
        return f'{chat_link} is a bad link'


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


def self_username():
    self_chat = chat('me')
    if self_chat.username:
        return 'https://t.me/' + self_chat.username
    else:
        phone_number = str(config.phone_number)
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        return 'https://t.me/' + phone_number


def set_logs_chat(
    _,
    msg: pyrogram.types.Message
):
    msg.reply(
        text = init_parse_link(
            chat_link = msg.text
        ),
        quote = True,
    )


def main() -> None:
    init_config()
    global bot
    global self_chat_handler
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
                text = f'''\
{start_message}

Please create new empty group chat and send here clickable link to it. This chat needed for logs and for configuring script. You must be an admin, and nobody except you must have access to this chat.

acceptable formats:
@chat_name
t.me/chat_name
t.me/+6XqO65TrfatjNGU6
webz.telegram.org/#-1657778608
'''
            )
        # for link in [
        #     # 'https://t.me/gmanka',
        #     # 't.me/sdasldkasldkas',
        #     # 't.me/+6XqO65TrfatjNGU6',
        #     'https://webz.telegram.org/#-1657778608'
        # ]:
        #     print(init_parse_link(link))

        print(f'\n[bold green]please open telegram and see your "saved messages" chat in telegram - [/bold green][bold]{self_username()}')

        self_chat_handler = bot.add_handler(
            MessageHandler(
                set_logs_chat
            )
        )
        pyrogram.idle()


main()
