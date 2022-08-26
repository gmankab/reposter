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
from pyrogram import filters, types
import gmanka_yml as yml
import pyrogram as pg
import subprocess
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
bot: pg.client.Client = None
get_chat: pg.client.Client.get_chat = None
send_msg: pg.client.Client.send_message = None

os_name = platform.system()
if os_name == 'Linux':
    os_name = platform.freedesktop_os_release()['PRETTY_NAME']
os_name = f'{os_name} {platform.release()}'
python_imp = f'{platform.python_implementation()} {platform.python_version()}'

app_full_name = f'''
gmanka {app_name} {app_version},
pg {pg.__version__},
{python_imp}\
'''

acceptable_link_formats = '''\
acceptable link formats:
@chat_name
t.me/chat_name
t.me/+6XqO65TrfatjNGU6
webz.telegram.org/#-1657778608
'''

if portable:
    app_full_name = f'portable {app_full_name}'

start_message = f'{app_full_name},\n{os_name}'


print(
    start_message,
    highlight = False,
)


def is_chat_exist(
    chat_id: str | int,
) -> types.Chat | bool:
    try:
        return get_chat(chat_id)
    except Exception as exception:
        return False


def is_group_owner(
    chat: types.Chat,
    chat_link: str,
) -> str | types.Chat:
    if isinstance(
        chat,
        str
    ):
        return chat
    if chat.type not in [
        pg.enums.ChatType.GROUP,
        pg.enums.ChatType.SUPERGROUP,
    ]:
        return f'{chat_link} is not a group chat'
    try:
        user: types.ChatMember = bot.get_chat_member(
            chat.id,
            'me',
        )
        if user.status != pg.enums.ChatMemberStatus.OWNER:
            return f'you are not an owner of {chat_link}'
    except pg.errors.exceptions.bad_request_400.UserNotParticipant:
        return f'you are not a member of {chat_link}'
    return chat


def get_chat_from_link(
    chat_link
) -> types.Chat:
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
            return get_chat(
                int(
                    chat_id.replace(
                        '-',
                        '-100',
                    )
                )
            )
    else:
        return get_chat(chat_link)


def parse_chat_link(
    chat_link: str
) -> types.Chat | str:
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
            return chat
        else:
            chat_id = chat_id.replace(
                '-',
                '-100',
            )
            chat = is_chat_exist(
                int(chat_id),
            )
            if chat:
                return chat
            else:
                return f'{chat_link} is a bad link'
    else:
        return f'{chat_link} is not a clickable telegram link {acceptable_link_formats}'
    chat = is_chat_exist(
        chat_link
    )
    if chat:
        return chat
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
    self_chat = get_chat('me')
    if self_chat.username:
        return 'https://t.me/' + self_chat.username
    else:
        phone_number = str(
            config.phone_number
        )
        for char in ' ()-_':
            phone_number = phone_number.replace(
                char,
                '',
            )
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        return 'https://t.me/' + phone_number


def init_set_logs_chat(
    _,
    msg: types.Message
):
    answer: types.Message = msg.reply(
        'applying...',
        quote = True,
        disable_web_page_preview = True,
    )

    chat_link = str(
        msg.text
    ).replace(
        'https://',
        '',
    ).replace(
        'http://',
        '',
    )

    chat = is_group_owner(
        parse_chat_link(
            chat_link
        ),
        chat_link,
    )

    if isinstance(
        chat,
        str,
    ):
        answer.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_logs_chat_handler()
        answer.edit_text(
            f'successfully set {chat_link} as chat for settings and logs, please open it',
            disable_web_page_preview = True,
        )


def set_logs_chat(
    _,
    msg: types.Message
):
    chat_link = split_message(msg)
    if not chat_link:
        return

    answer: types.Message = msg.reply(
        'applying...',
        quote = True,
        disable_web_page_preview = True,
    )

    chat = is_group_owner(
        parse_chat_link(
            chat_link
        ),
        chat_link,
    )

    if isinstance(
        chat,
        str,
    ):
        answer.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_logs_chat_handler()
        answer.edit_text(
            f'successfully set {chat_link} as chat for settings and logs, please open it',
            disable_web_page_preview = True,
        )


def help(
    _ = None,
    msg: types.Message = None,
    chat_id = None
) -> None:
    if msg:
        reply_msg_id = msg.id
        chat_id = msg.chat.id
    else:
        reply_msg_id = None

    send_msg(
        text = f'''
your config file path:
**{config_path}**

users, who can configure reposter:
can_configure = **{config.can_configure}**

can be changed via this commands:
/set_can_configure_only_me
/set_can_configure_all_members_of_this_chat

logs_chat = {config.logs_chat}

can be changed via this command:
/set_logs_chat PUT_LINK_TO_LOGS_CHAT_HERE

example:
/set_logs_chat {config.logs_chat}

you can see acceptable link formats via this command:
/show_acceptable_link_formats
''',
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
    )

    text = '''\
**source** chat is a chat from which messages are reposted
**target** chat is a chat in which messages are reposted
'''

    if config.chats_tree:
        for source, target in config.chats_tree.items():
            text += source
    else:
        text += '''
there is no source chat now, you can add add it via this command:
/set_new_source_chat PUT_SOURCE_CHAT_LINK_HERE
'''

    send_msg(
        text = text,
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
    )


def set_new_source_chat(
    _,
    msg: types.Message,
):
    chat_link = split_message(msg)
    if not chat_link:
        return

    answer: types.Message = msg.reply(
        'applying...',
        quote = True,
        disable_web_page_preview = True,
    )

    chat = parse_chat_link(
        chat_link
    )

    if isinstance(
        chat,
        str,
    ):
        answer.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        if chat_link in config.chats_tree:
            answer.edit_text(
                text = f'{chat_link} already in chats tree',
                disable_web_page_preview = True,
            )
            return

        config.chats_tree[chat_link] = {}
        config.to_file()
        answer.edit_text(
            f'successfully set {chat_link} as source chat',
            disable_web_page_preview = True,
        )


def split_message(
    msg: types.Message,
):
    msg_words = msg.text.split()
    match len(msg_words):
        case 1:
            msg.reply(
                'you must paste link to chat after "/set_logs_chat"',
                disable_web_page_preview = True,
            )
        case 2:
            return str(
                msg_words[-1]
            ).replace(
                'https://',
                '',
            ).replace(
                'http://',
                '',
            )
        case _:
            msg.reply(
                'you must paste only 1 link',
                disable_web_page_preview = True,
            )


def set_can_configure_all_members_of_this_chat(
    _,
    msg: types.Message,
):
    answer: types.Message = msg.reply(
        'applying...',
        quote = True,
    )

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
    msg: types.Message,
):
    answer: types.Message = msg.reply(
        'applying...',
        quote = True,
    )

    config['can_configure'] = 'only_me'
    refresh_handlers()
    answer.edit_text(
        f'''\
successfully set **can_configure** to **{config.can_configure}**
use /help to configure script
'''
    )


def show_acceptable_link_formats(
    _,
    msg: types.Message,
):
    msg.reply(
        text = acceptable_link_formats,
        quote = True,
    )


def refresh_handlers():
    logs_chat = temp_data['logs_chat']
    if not logs_chat:
        raise TypeError(
            'logs chat must be "types.Chat"'
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
        help:
            ['help', 'h'],
        set_can_configure_all_members_of_this_chat:
            'set_can_configure_all_members_of_this_chat',
        set_can_configure_only_me:
            'set_can_configure_only_me',
        show_acceptable_link_formats:
            'show_acceptable_link_formats',
        set_logs_chat:
            'set_logs_chat',
        set_new_source_chat:
            'set_new_source_chat',
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
    except pg.errors.exceptions.bad_request_400.UserNotParticipant:
        bot.add_chat_members(
            chat_id = logs_chat.id,
            user_ids = 'gmanka_bot',
            forward_limit = 0,
        )
        send_msg(
            text = 'invited @gmanka_bot just for make commands like /help clickable, he is not needed for anything else',
            chat_id = logs_chat.id,
        )

    send_msg(
        text = start_message + '\n\nuse /help to configure script',
        chat_id = logs_chat.id,
    )
    refresh_handlers()


def main() -> None:
    init_config()
    global bot
    global send_msg
    global get_chat
    if config['tg_session']:
        bot = pg.client.Client(
            name = app_name,
            session_string = config.tg_session,
        )
        first_start = False
    else:
        phone_number = str(config.phone_number)
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        bot = pg.client.Client(
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

    send_msg = bot.send_message
    get_chat = bot.get_chat

    with bot:
        if first_start:
            config['tg_session'] = bot.export_session_string()
        if not config['logs_chat']:
            print(f'\n[bold green]please open telegram and see your "saved messages" chat - [/bold green][bold]{self_username()}')

            send_msg(
                chat_id = 'me',
                disable_web_page_preview = True,
                text = f'''\
{start_message}

Please create new empty group chat and send here clickable link to it. This chat needed for logs and for configuring script. You must be an owner, and nobody except you must have access to this chat.

{acceptable_link_formats}
'''
            )

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

        pg.idle()


main()
