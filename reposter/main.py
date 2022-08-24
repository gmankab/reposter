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
from pyrogram import filters
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
config_path = Path(
    f'{proj_path}/config.yml'
)
config = Data(
    file_path = config_path
)

temp_data = Data()

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


def is_chat_exist(
    chat_id: str | int,
) -> pyrogram.types.Chat | bool:
    try:
        return bot.get_chat(chat_id)
    except Exception as exception:
        return False


def is_group(
    chat: pyrogram.types.Chat,
    chat_link,
) -> str | pyrogram.types.Chat:
    if chat.type not in [
        pyrogram.enums.ChatType.GROUP,
        pyrogram.enums.ChatType.SUPERGROUP,
    ]:
        return f'{chat_link} is not a group chat'
    try:
        bot.get_chat_member(
            chat.id,
            'me',
        )
    except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
        return f'you are not a member of {chat_link}'
    return chat


def get_chat_from_link(
    chat_link
) -> pyrogram.types.Chat:
    if (
        'webz.telegram.org/#' in chat_link
    ) or (
        'web.telegram.org/z/#' in chat_link
    ):
        chat_id = chat_link.rsplit(
            '#',
            1,
        )[-1]
        chat = is_chat_exist(
            int(chat_id),
        )
        if chat:
            return chat
        else:
            return bot.get_chat(
                int(
                    chat_id.replace(
                        '-',
                        '-100',
                    )
                )
            )
    else:
        return bot.get_chat(chat_link)


def parse_chat_link(
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
        chat = is_chat_exist(
            int(chat_id),
        )
        if chat:
            return is_group(chat, chat_link)
        else:
            chat_id = chat_id.replace(
                '-',
                '-100',
            )
            chat = is_chat_exist(
                int(chat_id),
            )
            if chat:
                return is_group(chat, chat_link)
            else:
                return f'{chat_link} is a bad link'
    else:
        return f'{chat_link} is not working telegram link'
    chat = is_chat_exist(
        chat_link
    )
    if chat:
        return is_group(chat, chat_link)
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
        if not config[item]:
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

    if not config['chats_tree']:
        config['chats_tree'] = {}

    if not config['can_configure']:
        config['can_configure'] = 'only_me'

    temp_data['handlers'] = []


def self_username():
    self_chat = bot.get_chat('me')
    if self_chat.username:
        return 'https://t.me/' + self_chat.username
    else:
        phone_number = str(config.phone_number)
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        return 'https://t.me/' + phone_number


def init_set_logs_chat(
    _,
    msg: pyrogram.types.Message
):
    answer = msg.reply('applying...')

    chat_link = msg.text
    chat = parse_chat_link(chat_link)

    if isinstance(
        chat,
        str,
    ):
        answer.edit_text(
            chat
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_logs_chat_handler()
        return f'successfully set {chat_link} as chat for settings and logs, please open it'

    answer.edit_text(
        text = parse_chat_link(
            chat_link = msg.text
        ),
        quote = True,
    )


def get_help(
    _ = None,
    msg: pyrogram.types.Message = None,
    chat_id = None
) -> None:
    if msg:
        reply_msg_id = msg.id
        chat_id = msg.chat.id
    else:
        reply_msg_id = None

    bot.send_message(
        text = f'''
your config file path:
**{config_path}**

users, who can configure reposter:
can_configure = **{config.can_configure}**
/set_can_configure_only_me
/set_can_configure_all_members_of_this_chat

logs_chat = {config.logs_chat}

can be changed via this command:
/set_logs_chat PUT_LOGS_CHAT_LINK_HERE

you can see acceptable link formats via this command:
/show_acceptable_links_formats
''',
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
    )

    bot.send_message(
        text = '''
**source** chat is a chat from which messages are reposted
**target** chat is a chat in which messages are reposted

there is no source chat now, you can add add it via this command:
/set_source_chat PUT_SOURCE_CHAT_LINK_HERE
''',
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
    )


def set_can_configure_all_members_of_this_chat(
    _,
    msg: pyrogram.types.Message,
):
    answer = msg.reply('applying...')
    config['can_configure'] = 'all_members'
    refresh_handlers()
    answer.edit_text(
        f'''\
successfully set **can_configure** to **{config.can_configure}**
use /help to configure script
'''
    )


def set_can_configure_only_me(
    _,
    msg: pyrogram.types.Message,
):
    answer = msg.reply('applying...')
    config['can_configure'] = 'only_me'
    refresh_handlers()
    answer.edit_text(
        f'''\
successfully set **can_configure** to **{config.can_configure}**
use /help to configure script
'''
    )


def refresh_handlers():
    logs_chat = temp_data['logs_chat']
    if not logs_chat:
        raise TypeError(
            'logs chat must be "pyrogram.types.Chat"'
        )
    for handler in temp_data.handlers:
        bot.remove_handler(*handler)
    temp_data['handlers'] = []

    def blank_filter(
        commands: list[str] | str,
    ):
        match config.can_configure:
            case 'only_me':
                return filters.chat(
                    logs_chat.id
                ) & filters.user(
                    'me'
                ) & filters.command(
                    commands
                )
            case 'all_members':
                return filters.chat(
                    logs_chat.id
                ) & filters.command(
                    commands
                )

    for func, commands in {
        get_help:
            ['help', 'h'],
        set_can_configure_all_members_of_this_chat:
            'set_can_configure_all_members_of_this_chat',
        set_can_configure_only_me:
            'set_can_configure_only_me',
    }.items():
        temp_data.handlers.append(
            bot.add_handler(
                MessageHandler(
                    func,
                    filters = blank_filter(
                        commands = commands
                    )
                )
            )
        )


def init_logs_chat_handler():
    logs_chat = temp_data['logs_chat']
    if not logs_chat:
        logs_chat = get_chat_from_link(
            config.logs_chat
        )
        temp_data['logs_chat'] = logs_chat

    try:
        bot.get_chat_member(
            logs_chat.id, 'gmanka_bot'
        )
    except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
        bot.add_chat_members(
            chat_id = logs_chat.id,
            user_ids = 'gmanka_bot',
            forward_limit = 0,
        )
        bot.send_message(
            text = 'invited @gmanka_bot just for make commands like /help clickable, he is not needed for anything else',
            chat_id = logs_chat.id,
        )

    bot.send_message(
        text = start_message + '\n\nuse /help to configure script',
        chat_id = logs_chat.id,
    )
    refresh_handlers()


def main() -> None:
    init_config()
    global bot
    if config['tg_session']:
        bot = pyrogram.client.Client(
            name = app_name,
            session_string = config.tg_session,
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
            config['tg_session'] = bot.export_session_string()
        if not config['logs_chat']:
            bot.send_message(
                chat_id = 'me',
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

            print(f'\n[bold green]please open telegram and see your "saved messages" chat - [/bold green][bold]{self_username()}')

            temp_data.handlers.append(
                bot.add_handler(
                    MessageHandler(
                        init_set_logs_chat,
                        filters = filters.chat('me'),
                    )
                )
            )
        else:
            print(f'\n[bold green]please open telegram and see your logs chat - [/bold green][bold]https://{config.logs_chat.replace("@", "t.me/")}')
            init_logs_chat_handler()

        pyrogram.idle()


main()
