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
from rich.tree import Tree
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
pp = pretty.pprint
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
pyrogram {pg.__version__},
{python_imp}\
'''

acceptable_link_formats = '''\
acceptable link formats:
@chat_name
t.me/chat_name
t.me/+6XqO65TrfatjNGU6
webz.telegram.org/#-1657778608
'''
acceptable_links_list = [
    '@chat_name',
    't.me/chat_name',
    't.me/+6XqO65TrfatjNGU6',
    'webz.telegram.org/#-1657778608',
]

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

    temp_data['config_handlers'] = []
    temp_data['reposter_handlers'] = []
    temp_data['chats_tree'] = {}


def self_username() -> None:
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
) -> None:
    reply = applying(msg)
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
        reply.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_handlers()
        reply.edit_text(
            f'successfully set {chat_link} as chat for settings and logs, please open it',
            disable_web_page_preview = True,
        )


def set_logs_chat(
    _,
    msg: types.Message
) -> None:
    chat_link = split_message(msg)
    if not chat_link:
        return

    reply = applying(msg)
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
        reply.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_handlers()
        reply.edit_text(
            f'successfully set {chat_link} as chat for settings and logs, please open it',
            disable_web_page_preview = True,
        )


def recursive_tree_builder(
    local_tree: Tree,
    local_tree_dict: dict,
    previous: list
) -> None:
    for chat_link, child_tree_dict in local_tree_dict.items():
        child_previous = previous.copy()
        child_previous.append(
            chat_link
        )
        child_tree = local_tree.add(
            label = f'`{chat_link}'
        )
        previous_str = " -> ".join(
            child_previous
        )
        if child_tree_dict:
            recursive_tree_builder(
                local_tree = child_tree,
                local_tree_dict = child_tree_dict,
                previous = child_previous,
            )
        else:
            remove_command = f'``/remove {previous_str}`'
            child_tree.add(
                remove_command
            )
        add_command = f'``/add_target {previous_str} -> TARGET`'
        child_tree.add(
            add_command
        )


def build_chat_tree() -> None:
    tree_dict = config.chats_tree
    tree = Tree(label = 'chats tree')
    recursive_tree_builder(
        local_tree = tree,
        local_tree_dict = tree_dict,
        previous = []
    )
    with c.capture() as capture:
        for child in tree.children:
            print(child)
    return '`' + capture.get().replace(
        '\n',
        '\n`'
    ).replace(
        '└',
        '╰'
    )[:-1]


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
`/set_logs_chat PUT_LINK_TO_LOGS_CHAT_HERE`

example:
/set_logs_chat {config.logs_chat}

you can see acceptable link formats via this command:
/show_acceptable_link_formats
''',
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
    )

    text = '''\
**source chat** is a chat from which messages reposted
**target chat** is a chat in which messages reposted
'''

    if config.chats_tree:
        text += '''
/remove CHAT_NAME - stop reposting from this chat and to this chat
/add_target SOURCE -> TARGET - add new target chat

chats tree:
'''
        text += build_chat_tree()
        text += '`/add_source SOURCE`'
    else:
        text += '''
there is no source chat now, you can add add it via this command:
`/add_source PUT_SOURCE_CHAT_LINK_HERE`
'''

    send_msg(
        text = text,
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
    )


def add_source(
    _,
    msg: types.Message,
) -> None:
    chat_link = split_message(msg)
    if not chat_link:
        return

    reply = applying(msg)
    chat = parse_chat_link(
        chat_link
    )

    if isinstance(
        chat,
        str,
    ):
        reply.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        if chat_link in config.chats_tree:
            reply.edit_text(
                text = f'{chat_link} already in chats tree',
                disable_web_page_preview = True,
            )
            return

        config.chats_tree[chat_link] = {}
        config.to_file()
        reply.edit_text(
            f'''
successfully added {chat_link} to chats tree

use /help to see updated chats tree
''',
            disable_web_page_preview = True,
        )


def split_message(
    msg: types.Message,
) -> str | None:
    msg_words = msg.text.split()
    match len(msg_words):
        case 1:
            text = f'''\
you must paste link to chat after "{msg.text}"

examples:
'''
            for link in acceptable_links_list:
                text += f'{msg.text} {link}\n'
            msg.reply(
                text,
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
) -> None:
    reply: types.Message = msg.reply(
        'applying...',
        quote = True,
    )

    config['can_configure'] = 'all_members'
    refresh_config_handlers()
    reply.edit_text(
        f'''\
successfully set **can_configure** to **{config.can_configure}**

use /help to configure reposter
'''
    )


def set_can_configure_only_me(
    _,
    msg: types.Message,
) -> None:
    reply: types.Message = msg.reply(
        'applying...',
        quote = True,
    )

    config['can_configure'] = 'only_me'
    refresh_config_handlers()
    reply.edit_text(
        f'''\
successfully set **can_configure** to **{config.can_configure}**

use /help to configure reposter
'''
    )


def show_acceptable_link_formats(
    _,
    msg: types.Message,
) -> None:
    msg.reply(
        text = acceptable_link_formats,
        quote = True,
    )


def applying(
    msg: types.Message
) -> types.Message:
    return msg.reply(
        text = 'applying...',
        quote = True,
    )


def add_target(
    _,
    msg: types.Message,
) -> None:
    chats_str = msg.text.split(
        maxsplit = 1
    )
    if len(
        chats_str
    ) == 1:
        msg.reply(
            text = '''
**source chat** is a chat from which messages reposted
**target chat** is a chat in which messages reposted

/add_target SOURCE TARGET - add new target chat',
''',
            quote = True,
        )
        return

    chats = chats_str[-1].split(
        ' -> '
    )
    if len(
        chats
    ) == 1:
        msg.reply(
            text = '''
**source chat** is a chat from which messages reposted
**target chat** is a chat in which messages reposted

you must paste at least 2 links after /add_target - source chat link and target chat link
'''
        )
        return

    reply = applying(msg)
    chats_tree = config.chats_tree
    for chat in chats[:-1]:
        if chat in chats_tree:
            chats_tree = chats_tree[chat]
        else:
            reply.edit_text(
                text = f'''\
can\'t find {chat} in chats tree

use /help to see chats tree
'''
            )
            return

    chat_link = chats[-1]

    chat = parse_chat_link(
        chat_link
    )

    if isinstance(
        chat,
        str,
    ):
        reply.edit_text(
            chat,
            disable_web_page_preview = True,
        )
    else:
        if chat_link in chats_tree:
            reply.edit_text(
                text = f'{chat_link} already in chats tree',
                disable_web_page_preview = True,
            )
            return

        chats_tree[
            chat_link
        ] = {}
        config.to_file()
        refresh_reposter_handlers()
        reply.edit_text(
            f'''
successfully added {chats[-1]} to chats tree

use /help to see updated chats tree
'''
        )


def remove(
    _,
    msg: types.Message,
) -> None:
    chats_str = msg.text.split(
        maxsplit = 1
    )
    if len(chats_str) == 1:
        msg.reply(
            '/remove CHAT_NAME - remove this chat from chats tree',
            quote = True,
        )
        return

    reply = applying(msg)
    chats = chats_str[-1].split(
        ' -> '
    )

    chats_tree = config.chats_tree
    for chat in chats[:-1]:
        if chat in chats_tree:
            chats_tree = chats_tree[chat]
        else:
            reply.edit_text(
                text = f'''\
can\'t find {chat} in chats tree

use /help to see chats tree
'''
            )
            return

    result = chats_tree.pop(
        chats[-1],
        None,
    )
    if result is None:
        reply.edit_text(
            f'''\
can't find {chats[-1]} in chats tree

use /help to see chats tree
'''
        )
    else:
        config.to_file()
        refresh_reposter_handlers()
        reply.edit_text(
            f'''
successfully removed {chats[-1]} from chats tree

use /help to see updated chats tree
'''
        )


def forward(
    msg: types.Message,
    target: int,
) -> types.Message:
    print(msg)
    new_msg = bot.send_message(
        text = msg.text,
        chat_id = target,
    )
    return new_msg


def resend(
    msg: types.Message,
    target: int,
) -> types.Message:
    pass


def recursive_repost(
    msg: types.Message,
    targets: dict,
) -> None:
    if not targets:
        return
    for key, val in targets.items():
        if msg.from_user.is_restricted:
            new_msg = resend(
                msg = msg,
                target = get_chat_from_link(
                    key,
                ).id,
            )
        else:
            new_msg = forward(
                msg = msg,
                target = get_chat_from_link(
                    key,
                ).id,
            )
        recursive_repost(
            msg = new_msg,
            targets = val
        )


def init_recursive_repost(
    _,
    msg: types.Message,
) -> None:
    targets: dict = temp_data.chats_tree[msg.chat.id]
    recursive_repost(
        msg = msg,
        targets = targets,
    )



def refresh_reposter_handlers() -> None:
    for handler in temp_data.reposter_handlers:
        bot.remove_handler(*handler)
    temp_data['reposter_handlers'] = []
    temp_data['chats_tree'] = {}

    for source_link, target in config.chats_tree.items():
        source = get_chat_from_link(source_link)
        temp_data.chats_tree[source.id] = target

        temp_data.reposter_handlers.append(
            bot.add_handler(
                MessageHandler(
                    init_recursive_repost,
                    filters = filters.chat(
                        source.id
                    )
                )
            )
        )


def refresh_config_handlers() -> None:
    logs_chat = temp_data['logs_chat']
    for handler in temp_data.config_handlers:
        bot.remove_handler(*handler)
    temp_data['config_handlers'] = []

    def blank_filter(
        commands: list[str] | str,
    ) -> None:
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

    def new_handler(
        func,
        commands: list[str] | str,
    ) -> None:
        temp_data.config_handlers.append(
            bot.add_handler(
                MessageHandler(
                    func,
                    filters = blank_filter(
                        commands = commands
                    )
                )
            )
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
        add_source:
            'add_source',
        add_target:
            'add_target',
        remove:
            'remove',
    }.items():
        new_handler(
            func = func,
            commands = commands,
        )


def init_handlers() -> None:
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
        text = start_message + '\n\nuse /help to configure reposter',
        chat_id = logs_chat.id,
    )
    refresh_config_handlers()
    refresh_reposter_handlers()


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

Please create new empty group chat and send here clickable link to it. This chat needed for logs and for configuring reposter. You must be an owner, and nobody except you must have access to this chat.

{acceptable_link_formats}
'''
            )

            temp_data.config_handlers.append(
                bot.add_handler(
                    MessageHandler(
                        init_set_logs_chat,
                        filters = filters.chat('me'),
                    )
                )
            )
        else:
            print(f'\n[bold green]please open telegram and see your logs chat - [/bold green][bold]https://{config.logs_chat.replace("@", "t.me/")}')
            init_handlers()

        pg.idle()


main()
