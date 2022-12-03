# license: gnu gpl 3 https://gnu.org/licenses/gpl-3.0.en.html
# sources: https://github.com/gmankab/reposter

try:
    from setup import (  # type: ignore
        modules_path,
        win_py_file,
        app_version,
        yes_or_no,
        proj_path,
        app_name,
        portable,
        os_name,
        run,
    )
except ModuleNotFoundError:
    from reposter.setup import (  # type: ignore
        modules_path,
        win_py_file,
        app_version,
        yes_or_no,
        proj_path,
        app_name,
        portable,
        os_name,
        run,
    )

import rich.pretty
import rich.progress
import rich.traceback
import rich.tree
from pathlib import Path
from betterdata import Data
from pyrogram.handlers import (
    MessageHandler,
    EditedMessageHandler,
    DeletedMessagesHandler,
)
from pyrogram import (
    filters,
    types,
    errors,
)
from urllib import request as r
import gmanka_yml as yml
import pyrogram as pg
import humanize
import platform
import hashlib
import rich
import time
import json
import sys
import os


class PollException(Exception):
    pass


class UnsupportedException(Exception):
    pass


rich.pretty.install()
rich.traceback.install(
    show_locals=True
)
c = rich.console.Console(
    width=80
)
cache_path = Path(
    f'{modules_path}/{app_name}_tg_chache'
)
config_path = Path(
    f'{modules_path}/{app_name}.yml'
)
history_path = Path(
    f'{modules_path}/msg_history.yml'
)
log_path = Path(
    f'{modules_path}/{app_name}.log'
)
config = Data(
    file_path=config_path
)
history = Data(
    file_path=history_path
)
temp_data = Data()

c_log = None
print = c.print
log = c.log
pp = rich.pretty.pprint
bot: pg.client.Client = None
if os_name == 'Linux':
    try:
        os_name = platform.freedesktop_os_release()['PRETTY_NAME']
    except Exception:
        pass
os_name = f'{os_name} {platform.release()}'
python_imp = f'{platform.python_implementation()} {platform.python_version()}'
pip = f'{sys.executable} -m pip'


app_full_name = f'''\
gmanka {app_name} {app_version},
pyrogram {pg.__version__},
{python_imp}\
'''

acceptable_link_formats = '''\
acceptable link formats:
@chat_name
t.me/chat_name
t.me/+6XqO65TrfatjNGU6
web.telegram.org/k/#-1657778608
'''
acceptable_links_examples = [
    '@chat_name',
    't.me/chat_name',
    't.me/+6XqO65TrfatjNGU6',
    'web.telegram.org/k/#-1657778608',
]

if portable:
    app_full_name = f'portable {app_full_name}'

start_message = f'''\
{app_full_name},
{os_name},
config path - {config_path}
'''


log(
    start_message,
    highlight=False,
)


def is_chat_exist(
    chat_id: str | int,
) -> types.Chat | bool:
    try:
        return bot.get_chat(chat_id)
    except Exception:
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
    except errors.exceptions.bad_request_400.UserNotParticipant:
        return f'you are not a member of {chat_link}'
    return chat


def get_chat_from_id(
    chat_id: str | int
):
    chat_id = str(chat_id)
    chat = is_chat_exist(
        int(chat_id),
    )
    if chat:
        return chat
    if '-' not in chat_id:
        chat_id = f'-{chat_id}'
    chat = is_chat_exist(
        int(chat_id),
    )
    if chat:
        return chat
    return bot.get_chat(
        int(
            chat_id.replace(
                '-',
                '-100',
            )
        )
    )


def get_chat_from_link(
    chat_link
) -> types.Chat:
    if '.telegram.org/' in chat_link:
        chat_id = chat_link.rsplit(
            '#',
            1,
        )[-1]
        return get_chat_from_id(
            chat_id
        )
    else:
        return bot.get_chat(
            chat_link
        )


def get_hash(
    string: str
):
    hash = hashlib.new('sha256')
    hash.update(
        string.encode()
    )
    return hash.hexdigest()


def parse_chat_link(
    chat_link: str
) -> types.Chat | str:
    if not chat_link:
        return chat_link
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
    elif '.telegram.org/' in chat_link:
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
        return f'{chat_link} is not a clickable telegram link\n\n{acceptable_link_formats}'
    chat = is_chat_exist(
        chat_link
    )
    if chat:
        return chat
    else:
        return f'{chat_link} is a bad link'


def init_config() -> None:
    if (
        config['app_version']
    ) and (
        config['app_version'] < '22.1.21'
    ):
        config['app_version'] = app_version
        # update forced because of very important bugfix
        update_app(
            forced=True
        )
    if (
        config['app_version']
    ) and (
        config['app_version'] < '22.3.5'
    ) and portable:
        bat_file = Path(f'{modules_path.parent.resolve()}/{app_name}.bat')
        bat_file_tmp = Path(f'{bat_file}.tmp')
        win_py_file_tmp = Path(f'{win_py_file}.tmp')
        old_python_path = Path(f'{modules_path}/.python_3.10.7')
        r.urlretrieve(
            url='https://raw.githubusercontent.com/gmankab/{app_name}/main/launcher/{app_name}.bat',
            filename = bat_file_tmp,
        )
        r.urlretrieve(
            url='https://raw.githubusercontent.com/gmankab/{app_name}/main/launcher/{app_name}_win.py',
            filename = win_py_file_tmp,
        )
        if (
            win_py_file_tmp.exists()
        ) and (
            bat_file_tmp.exists()
        ):
            bat_file.unlink(
                missing_ok = True
            )
            bat_file_tmp.rename(
                bat_file
            )
            win_py_file.unlink(
                missing_ok = True
            )
            win_py_file_tmp.rename(
                win_py_file
            )
        config['app_version'] = app_version
        restart_command = f'''\
taskkill /f /pid {os.getpid()} && \
rd /s /q "{old_python_path}" & \
timeout /t 1 && \
{bat_file}\
'''
        print(
            f'restarting and updating {app_name} with command:\n{restart_command}'
        )
        os.system(
            restart_command
        )

    elif config['app_version'] != app_version:
        config['app_version'] = app_version

    if 'check_updates' not in config:
        if yes_or_no.choose(
            text='[deep_sky_blue1]do you want to check updates on start?'
        ) == 'yes':
            config['check_updates'] = True
        else:
            config['check_updates'] = False

    if (
        not config['api_id']
    ) or (
        not config['api_hash']
    ):
        print(
            '\nPlease open https://my.telegram.org/apps and get api_id and api_hash')
        print(
            '''\
[bold red]WARNING:[/bold red] [bold white]use only your own api_id and api_hash.[/bold white] I already tried to take them from decompiled official telegram app, and 20 minutes later my telegram account get banned. Then I wrote email with explanation on recover@telegram.org and on the next day and they unbanned me.
''', highlight=False
        )

    for item in (
        'api_id',
        'api_hash',
        'phone_number',
    ):
        config.interactive_input(item)

    if 'edited_history' not in config:
        config['edited_history'] = True
    if 'chats_tree' not in config:
        config['chats_tree'] = {}
    if 'can_configure' not in config:
        config['can_configure'] = 'only_me'
    if 'stream_notifications' not in config:
        config['stream_notifications'] = []
    if 'repeat_notifications' not in config:
        config['repeat_notifications'] = 75
    if 'notifications_delay' not in config:
        config['notifications_delay'] = 3
    temp_data['config_handlers'] = []
    temp_data['reposter_handlers'] = []
    temp_data['chats_tree'] = {}
    temp_data['links'] = {}
    temp_data['media_groups'] = {}


def self_username() -> None:
    self_chat = temp_data.me
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
    if msg.chat.id != temp_data.me.id:
        return
    reply = applying(msg)
    chat_link = clean_link(
        msg.text
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
            disable_web_page_preview=True,
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_handlers()
        reply.edit_text(
            f'successfully set {chat_link} as chat for settings and logs, please open it',
            disable_web_page_preview=True,
        )


def set_logs_chat(
    _,
    msg: types.Message
) -> None:
    chat_link = split_msg(msg)
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
            disable_web_page_preview=True,
        )
    else:
        temp_data['logs_chat'] = chat
        config['logs_chat'] = chat_link
        init_handlers()
        reply.edit_text(
            f'successfully set {chat_link} as chat for settings and logs, please open it',
            disable_web_page_preview=True,
        )


def recursive_tree_builder(
    local_tree: rich.tree.Tree,
    local_tree_dict: dict,
    previous: list
) -> None:
    for chat_link, child_tree_dict in local_tree_dict.items():
        child_previous = previous.copy()
        child_previous.append(
            chat_link
        )
        child_tree = local_tree.add(
            label=f'`{chat_link}'
        )
        previous_str = " -> ".join(
            child_previous
        )
        if child_tree_dict:
            recursive_tree_builder(
                local_tree=child_tree,
                local_tree_dict=child_tree_dict,
                previous=child_previous,
            )
        else:
            remove_command = f'`[/remove {previous_str}]'
            child_tree.add(
                remove_command
            )
        add_command = f'`[/add_target {previous_str} -> TARGET]'
        child_tree.add(
            add_command
        )


def build_chat_tree() -> None:
    tree_dict = config.chats_tree
    tree = rich.tree.Tree(label='chats tree', hide_root=True)
    recursive_tree_builder(
        local_tree=tree,
        local_tree_dict=tree_dict,
        previous=[]
    )
    with c.capture() as capture:
        c.print(
            tree,
            markup=False,
        )

    tree = capture.get()

    while '[' in tree:
        start = tree.find('[')
        end = tree.find(']')
        peace = tree[start:end + 1]

        new_peace = peace
        for i in (
            '\n',
            '│       ',
            '│   ',
        ):
            while i in new_peace:
                new_peace = new_peace.replace(
                    i,
                    ''
                )

        tree = tree.replace(
            peace,
            new_peace.replace(
                '[',
                '`',
            ).replace(
                ']',
                '`',
            )
        )

    return '`' + tree.replace(
        '\n',
        '\n`'
    ).replace(
        '└',
        '╰'
    )[:-1]


def help(
    _ = None,
    msg: types.Message = None,
    chat_id = None,
) -> None:
    if msg:
        reply_msg_id = msg.id
        chat_id = msg.chat.id
    else:
        reply_msg_id = None

    text = f'''
your config file path:
`{config_path}`

users, who can configure reposter:
can_configure = **{config.can_configure}**

can be changed via this commands:
/set_can_configure_only_me
/set_can_configure_all_members_of_this_chat

save_edited_messages_history = **{config.edited_history}**

can be changed via this commands:
/save_edited_messages_history
/do_not_save_edited_messages_history

logs_chat = {config.logs_chat}

can be changed via this command:
`/set_logs_chat CHAT_LINK`

example:
/set_logs_chat {config.logs_chat}

repost all messages starting from specified one:
/repost **LINK**

example:
/repost t.me/c/1363784954/1969246
'''

    if config['stream_notifications']:
        text += '\nchats for stream notifications:\n'
        for link in config['stream_notifications']:
            text += f'  {link}\n'

    text += f'''
add chat for stream notifications:
`/set_stream_notifications CHAT_LINK`

remove:
`/remove_stream_notifications CHAT_LINK`

examples:
/set_stream_notifications {config.logs_chat}
/remove_stream_notifications {config.logs_chat}

notification will be repeated **{config['repeat_notifications']}** times
can be changed via this command:
`/set_repeat_notifications NUMBER`

example:
/set_repeat_notifications 10

you can see acceptable link formats via this command:
/show_acceptable_link_formats
'''
    bot.send_message(
        chat_id = chat_id,
        text = text,
        reply_to_message_id = reply_msg_id,
        disable_web_page_preview = True
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

    bot.send_message(
        text = text,
        reply_to_message_id = reply_msg_id,
        chat_id = chat_id,
        disable_web_page_preview = True,
    )


def repost_specified(
    _,
    msg: types.Message,
) -> None:
    answer: types.Message = msg.reply(
        text = 'starting...'
    )
    splitted = msg.text.split('/')
    if len(splitted) < 3:
        answer.edit(
            text = 'you must specify link to message after /repost'
        )
        return
    msg_id = int(splitted[-1])
    chat = get_chat_from_id(
        splitted[-2]
    )
    ids = []
    for msg in bot.get_chat_history(
        chat_id = chat.id,
    ):
        if msg.id < msg_id:
            break
        ids.append(msg.id)
    c.log(ids)
    for msg_id in reversed(ids):
        msg = bot.get_messages(
            chat_id = chat.id,
            message_ids = msg_id,
        )
        init_recursive_repost(
            _,
            src_msg = msg,
            force = True,
        )

    answer.reply(
        text = 'done',
        quote = True,
    )


def add_source(
    _,
    msg: types.Message,
) -> None:
    chat_link = split_msg(msg)
    if not chat_link:
        return

    chat_link = clean_link(chat_link)

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
            disable_web_page_preview=True,
        )
    else:
        if chat_link in config.chats_tree:
            reply.edit_text(
                text=f'{chat_link} already in chats tree',
                disable_web_page_preview=True,
            )
            return

        config.chats_tree[chat_link] = {}
        config.to_file()
        reply.edit_text(
            f'''
successfully added {chat_link} to chats tree

use /help to see updated chats tree
''',
            disable_web_page_preview=True,
        )


def split_msg(
    msg: types.Message,
) -> str | None:
    msg_words = msg.text.split()
    match len(msg_words):
        case 1:
            text = f'''\
you must paste link to chat after "{msg.text}"

examples:
'''
            for link in acceptable_links_examples:
                text += f'{msg.text} {link}\n'
            msg.reply(
                text,
                disable_web_page_preview=True,
            )
        case 2:
            return clean_link(
                msg_words[-1]
            )
        case _:
            msg.reply(
                'you must paste only 1 link',
                disable_web_page_preview=True,
            )


def set_can_configure_all_members_of_this_chat(
    _,
    msg: types.Message,
) -> None:
    reply: types.Message = msg.reply(
        'applying...',
        quote=True,
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
        quote=True,
    )

    config['can_configure'] = 'only_me'
    refresh_config_handlers()
    reply.edit_text(
        f'''\
successfully set **can_configure** to **{config.can_configure}**

use /help to configure reposter
'''
    )


def set_stream_notifications(
    _,
    msg: types.Message,
) -> None:
    chat_link = split_msg(msg)
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
            disable_web_page_preview=True,
        )
    else:
        if chat_link in config['stream_notifications']:
            reply.edit_text(
                'chat already in list'
            )
        else:
            config['stream_notifications'].append(
                chat_link
            )
            refresh_stream_notifications()
            reply.edit_text(
                f'''
successfully added {chat_link} in notifications list

use /help to see list
''',
                disable_web_page_preview=True,
            )
            config.to_file()

def remove_stream_notifications(
    _,
    msg: types.Message,
) -> None:
    chat_link = split_msg(msg)
    reply = applying(msg)
    if chat_link in config['stream_notifications']:
        config['stream_notifications'].remove(
            chat_link
        )
        refresh_stream_notifications()
        reply.edit_text(
            f'''
successfully removed {chat_link} from notifications list

use /help to see list
''',
            disable_web_page_preview=True,
        )
        config.to_file()
    else:
        reply.edit_text(
            'chat not in list'
        )


def refresh_stream_notifications():
    temp_data['stream_notifications'] = []
    for user in config['stream_notifications']:
        chat = parse_chat_link(user)
        if isinstance(chat, str):
            bot.send_message(
                temp_data['logs_chat'],
                chat,
            )
        else:
            temp_data['stream_notifications'].append(
                chat
            )


def set_repeat_notifications(
    _,
    msg: types.Message,
) -> None:
    reply: types.Message = msg.reply(
        'applying...',
        quote=True,
    )
    splitted = msg.text.split()
    match len(splitted):
        case 1:
            reply.edit(
                text = f'''\
you must paste number after "{msg.text}"

example:
{msg.text} 10
'''
            )
            return
        case 2:
            pass
        case _:
            reply.edit(
                text = 'you must paste only 1 number'
            )
            return
    number = splitted[-1]
    if number.isdigit():
        config['repeat_notifications'] = int(number)
        reply.edit(
            text = f'''
now notifications will repeat {config.repeat_notifications} times

use /help to get help
'''
        )
    else:
        reply.edit(
            text = f'''\
you must paste number after "{msg.text}"

example:
{msg.text} 10
'''
        )


def set_save_edited_messages_history(
    _,
    msg: types.Message,
) -> None:
    reply: types.Message = msg.reply(
        'applying...',
        quote=True,
    )

    config['edited_history'] = True
    refresh_config_handlers()
    reply.edit_text(
        f'''\
successfully set **save_edited_messages_history** to **{config.edited_history}**

use /help to configure reposter
'''
    )


def set_do_not_save_edited_messages_history(
    _,
    msg: types.Message,
) -> None:
    reply: types.Message = msg.reply(
        'applying...',
        quote=True,
    )

    config['edited_history'] = False
    refresh_config_handlers()
    reply.edit_text(
        f'''\
successfully set **save_edited_messages_history** to **{config.edited_history}**

use /help to configure reposter
'''
    )


def show_acceptable_link_formats(
    _,
    msg: types.Message,
) -> None:
    msg.reply(
        text=acceptable_link_formats,
        quote=True,
    )


def applying(
    msg: types.Message
) -> types.Message:
    return msg.reply(
        text='applying...',
        quote=True,
    )


def add_target(
    _,
    msg: types.Message,
) -> None:
    splitted_msg = msg.text.split(
        maxsplit=1
    )
    if len(
        splitted_msg
    ) == 1:
        msg.reply(
            text='''
**source chat** is a chat from which messages reposted
**target chat** is a chat in which messages reposted

/add_target SOURCE TARGET - add new target chat',
''',
            quote=True,
        )
        return

    chats = splitted_msg[-1].split(
        ' -> '
    )
    if len(
        chats
    ) == 1:
        msg.reply(
            text='''
**source chat** is a chat from which messages reposted
**target chat** is a chat in which messages reposted

you must paste at least 2 links after /add_target - source chat link and target chat link
'''
        )
        return

    chats[-1] = clean_link(chats[-1])
    reply = applying(msg)
    chats_tree = config.chats_tree
    for chat in chats[:-1]:
        if chat in chats_tree:
            chats_tree = chats_tree[chat]
        else:
            reply.edit_text(
                text=f'''\
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
            disable_web_page_preview=True,
        )
    else:
        if chat_link in chats_tree:
            reply.edit_text(
                text=f'{chat_link} already in chats tree',
                disable_web_page_preview=True,
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
        maxsplit=1
    )
    if len(chats_str) == 1:
        msg.reply(
            '/remove CHAT_NAME - remove this chat from chats tree',
            quote=True,
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
                text=f'''\
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
    log_msg: types.Message = None,
    reply_to_msg: int = None,
) -> types.Message:
    if msg.venue:
        # pyrogram can't copy venue, so reposter resending it
        return resend(
            msg=msg,
            target=target,
            log_msg=log_msg,
            reply_to_msg=reply_to_msg,
        )
    try:
        return msg.copy(
            chat_id=target,
            reply_to_message_id=reply_to_msg,
        )
    except errors.exceptions.bad_request_400.MediaInvalid:
        if msg.poll:
            log_msg.reply(
                text='pyrogram lib can\'t copy and send polls to private chats, so reposter will forward it',
                quote=True,
            )
            return msg.forward(
                chat_id=target,
            )
        else:
            raise
    except errors.exceptions.bad_request_400.MediaCaptionTooLong:
        log_msg.reply(
            text='pyrogram lib can\'t forward long messages without author, so reposter forward it',
            quote=True,
        )
        return msg.forward(
            chat_id=target,
        )


def text_wrap(
    text: str,
    chunk_size: int = 1024,
):
    for chunk_start in range(
        0,
        len(text),
        chunk_size
    ):
        yield text[
            chunk_start:chunk_start + chunk_size
        ]


def resend_file(
    msg: types.Message,
    log_msg: types.Message,
    file: types.Document,
    send_method,
    caption: str = None,
    target: int = None,
    width: int = None,
    height: int = None,
    max_size=1024 * 1024 * 100,
) -> types.Message | types.Document:
    latest_percent = None
    downloaded_file_path = None
    humanized_size = humanize.naturalsize(
        file.file_size
    )
    progress_action = 'downloading'
    progress_msg: types.Message = log_msg.reply(
        text=f'downloading {humanized_size} file...',
        quote=True,
    )

    def bot_progress(
        current: int,
        total: int,
    ):
        nonlocal progress_msg, latest_percent, progress_action
        percent = round(current / total * 100)
        if latest_percent != percent:
            latest_percent = percent
            progress_msg = progress_msg.edit_text(
                text = f'{progress_action} {humanized_size} file:\n{percent}%'
            )

    if file.file_size < max_size:
        downloaded_file = msg.download(
            in_memory = True,
            progress = bot_progress,
            block = True,
        )
    else:
        cache_path.mkdir(
            exist_ok = True,
            parents = True,
        )

        downloaded_file_path = f'{cache_path}/{msg.chat.id}_{msg.id}'
        if msg.photo:
            downloaded_file_path += '.jpg'
        elif 'file_name' in file.__dict__.keys():
            downloaded_file_path += f'_{file.file_name}'
        downloaded_file_path = Path(downloaded_file_path)

        downloaded_file = msg.download(
            progress=bot_progress,
            file_name=downloaded_file_path,
            in_memory=False,
            block=True,
        )

    progress_action = 'uploading'
    progress_msg: types.Message = log_msg.reply(
        text=f'uploading {humanized_size} file...',
        quote=True,
    )
    kwargs = {}
    args = []
    if caption:
        kwargs['caption'] = caption
    if width:
        kwargs['width'] = width
    if height:
        kwargs['height'] = height
    if target:
        args.append(target)
    else:
        kwargs['quote'] = True

    new_msg: types.Message = send_method(
        *args,
        downloaded_file,
        progress=bot_progress,
        **kwargs,
    )

    if downloaded_file_path:
        downloaded_file_path.unlink(
            missing_ok=True,
        )
    return new_msg


def resend(
    msg: types.Message,
    target: int,
    log_msg: types.Message,
    reply_to_msg=None,
) -> types.Message:
    if msg.caption:
        captions = list(
            text_wrap(
                msg.caption
            )
        )
        first_caption = captions[0]
        other_captions = captions[1:]
    else:
        first_caption = None
        other_captions = []

    kwargs = {
        'msg': msg,
        'target': target,
        'log_msg': log_msg,
        'caption': first_caption,
    }

    if msg.poll:
        try:
            options = []
            for option in msg.poll.options:
                options.append(
                    option.text
                )
            new_msg = bot.send_poll(
                chat_id=target,
                question=msg.poll.question,
                options=options,
                allows_multiple_answers=msg.poll.allows_multiple_answers,
            )
        except Exception as exc:
            raise PollException from exc
    elif msg.document:
        new_msg = resend_file(
            **kwargs,
            file=msg.document,
            send_method=bot.send_document,
        )
    elif msg.photo:
        new_msg = resend_file(
            **kwargs,
            file=msg.photo,
            send_method=bot.send_photo,
        )
    elif msg.video:
        new_msg = resend_file(
            **kwargs,
            file=msg.video,
            send_method=bot.send_video,
            width=msg.video.width,
            height=msg.video.height,
        )
    elif msg.video_note:
        new_msg = resend_file(
            **kwargs,
            file=msg.video_note,
            send_method=bot.send_video_note,
        )
    elif msg.voice:
        new_msg = resend_file(
            **kwargs,
            file=msg.voice,
            send_method=bot.send_voice,
        )
    elif msg.audio:
        new_msg = resend_file(
            **kwargs,
            file=msg.audio,
            send_method=bot.send_audio,
        )
    elif msg.animation:
        new_msg = resend_file(
            **kwargs,
            file=msg.animation,
            send_method=bot.send_animation,
            width=msg.animation.width,
            height=msg.animation.height,
        )
    elif msg.location:
        new_msg = bot.send_location(
            chat_id=target,
            latitude=msg.location.latitude,
            longitude=msg.location.longitude,
        )
    elif msg.venue:
        foursquare_id = msg.venue.foursquare_id or ""
        foursquare_type = msg.venue.foursquare_type or ""
        new_msg = bot.send_venue(
            chat_id=target,
            latitude=msg.venue.location.latitude,
            longitude=msg.venue.location.longitude,
            title=msg.venue.title,
            address=msg.venue.address,
            foursquare_id=foursquare_id,
            foursquare_type=foursquare_type,
            reply_to_message_id=reply_to_msg,
        )
    elif msg.contact:
        new_msg = bot.send_contact(
            chat_id=target,
            phone_number=msg.contact.phone_number,
            first_name=msg.contact.first_name,
            last_name=msg.contact.last_name,
            vcard=msg.contact.vcard,
        )
    elif msg.sticker:
        new_msg = bot.send_sticker(
            chat_id=target,
            sticker=msg.sticker.file_id,
        )
    elif msg.text:
        new_msg = bot.send_message(
            text=msg.text,
            chat_id=target,
        )
    elif msg.media:
        raise UnsupportedException(
            f'media type {msg.media} is unsupported by reposter'
        )
    else:
        raise UnsupportedException(
            'this message is unsupported by reposter'
        )
    for caption in other_captions:
        new_msg.reply(
            text=caption,
            quote=True,
        )
    return new_msg


def print_poll_exception(
    src_link,
    target_link,
    local_chats_tree,
    log_msg,
) -> types.Message:
    text = f'''
reposter can't repost polls from restricted chat to private chats

unfortunately, {src_link} is a restricted chat, and {target_link} is a private chat

skipping this step, trying repost from {src_link} to {", ".join(local_chats_tree.keys())}
'''
    return log_msg.reply(
        text=text,
        quote=True,
        disable_web_page_preview=True,
    )


def edit(
    target_id,
    msg_in_history,
    src_msg,
) -> bool | types.Message:
    target_msg: types.Message = bot.get_messages(
        chat_id=target_id,
        message_ids=msg_in_history[target_id],
    )
    if src_msg.text != target_msg.text:
        new_msg = target_msg.edit_text(
            src_msg.text
        )
    elif src_msg.caption != target_msg.caption:
        new_msg = target_msg.edit_caption(
            src_msg.caption
        )
    else:
        return False
    return new_msg


def resend_all(
    is_media_group,
    src_msg,
    target_id,
    log_msg,
    orig,
    msg_in_history,
) -> bool | types.Message:
    try:
        if is_media_group:
            new_msg = resend_media_group(
                src_media=src_msg.get_media_group(),
                target=target_id,
                log_msg=log_msg,
            )
            new_media_group = new_msg.get_media_group()
            orig_media_group = orig.get_media_group()
            for i in range(len(orig_media_group)):
                _orig_msg = orig_media_group[i]
                _new_msg = new_media_group[i]
                history[_orig_msg.chat.id][_orig_msg.id][
                    target_id
                ] = _new_msg.id
            history.to_file()
            return new_msg
        else:
            new_msg = resend(
                msg=src_msg,
                target=target_id,
                log_msg=log_msg,
            )
            msg_in_history[
                target_id
            ] = new_msg.id
            history.to_file()
            return new_msg
    except PollException:
        return False


def save_edited_history(
    target_id,
    msg_in_history,
    new_msg,
    src_msg,
    forward_func,
    log_msg,
    is_media_group,
) -> str:
    target_msg = msg_in_history[target_id]
    if is_media_group:
        target_msg = bot.get_messages(
            chat_id=target_id,
            message_ids=target_msg
        ).get_media_group()[0].id
    try:
        chat_msg: types.Message = bot.get_discussion_message(
            chat_id=target_id,
            message_id=target_msg,
        )
    except Exception as exc:
        # if not a channel or if has not linked chat
        log_msg.reply(
            text=f'can\'t get linked chat message:\n\n {exc}',
            quote=True,
        )
        return clean_link(
            new_msg.link
        )
    else:
        info_msg: types.Message = chat_msg.reply(
            f'{humanize.ordinal(msg_in_history["edited_times"])} message version:'
        )
        return clean_link(
            forward_func(
                msg=src_msg,
                target=info_msg.chat.id,
                reply_to_msg=info_msg.id,
            ).link
        )


def forward_all(
    src_msg,
    target_id,
    log_msg,
    msg_in_history,
    is_media_group,
    orig,
) -> types.Message:
    if is_media_group:
        new_msg: types.Message = forward_media_group(
            msg=src_msg,
            target=target_id,
            log_msg=log_msg,
        )
        new_media_group = new_msg.get_media_group()
        orig_media_group = orig.get_media_group()
        for i in range(len(orig_media_group)):
            _orig_msg = orig_media_group[i]
            _new_msg = new_media_group[i]
            history[_orig_msg.chat.id][_orig_msg.id][
                target_id
            ] = _new_msg.id
        history.to_file()
    else:
        new_msg: types.Message = forward(
            msg=src_msg,
            target=target_id,
            log_msg=log_msg,
        )
        msg_in_history[
            target_id
        ] = new_msg.id
        history.to_file()
    return new_msg


def mark_deleted(
    target_id,
    msg_in_history,
    log_msg,
    is_media_group,
) -> str:
    target_msg = msg_in_history[target_id]
    if is_media_group:
        target_msg = bot.get_messages(
            chat_id=target_id,
            message_ids=target_msg
        ).get_media_group()[0].id
    text = 'message deleted'
    new_msg = bot.send_message(
        chat_id=target_id,
        text=text,
        reply_to_message_id=target_msg,
    )
    try:
        chat_msg: types.Message = bot.get_discussion_message(
            chat_id=target_id,
            message_id=target_msg,
        )
    except Exception as exc:
        # if not a channel or if has not linked chat
        log_msg.reply(
            text=f'can\'t get linked chat message:\n\n {exc}',
            quote=True,
        )
        return new_msg
    else:
        chat_msg.reply(
            text=text,
            quote=True,
        )
        return new_msg


def recursive_repost(
    src_msg: types.Message,
    orig: types.Message,
    targets: list[dict],
    log_msg: types.Message,
    src_link: str,
    edited: bool,
    deleted: bool,
    msg_text = None,
) -> None:
    if not targets:
        return
    is_media_group = bool(
        src_msg.media_group_id
    )
    if is_media_group:
        forward_func = forward_media_group
    else:
        forward_func = forward
    restricted = bool(
        (
            src_msg.sender_chat
        ) and (
            src_msg.sender_chat.has_protected_content
        )
    )
    success = True
    msg_in_history = history[orig.chat.id][orig.id]
    for target in targets:
        target_link = target['link']
        next_chats_tree = target['next_chats_tree']
        target_id: int = target['chat'].id
        if msg_text:
            new_msg = bot.send_message(
                target_id,
                msg_text,
            )
        elif edited:
            new_msg = edit(
                target_id,
                msg_in_history,
                src_msg,
            )
        elif deleted:
            new_msg = mark_deleted(
                target_id,
                msg_in_history,
                log_msg,
                is_media_group,
            )
        else:
            if restricted:
                new_msg = resend_all(
                    is_media_group,
                    src_msg,
                    target_id,
                    log_msg,
                    orig,
                    msg_in_history,
                )
                if not new_msg:
                    print_poll_exception(
                        src_link,
                        target_link,
                        next_chats_tree,
                        log_msg,
                    )
                    new_msg = src_msg
                    new_log_msg = log_msg
            if not restricted:
                new_msg = forward_all(
                    src_msg,
                    target_id,
                    log_msg,
                    msg_in_history,
                    is_media_group,
                    orig,
                )
        if (
            success
        ) and (
            not restricted
        ) and (
            not deleted
        ) and (
            config.edited_history
        ):
            save_edited_history(
                target_id,
                msg_in_history,
                new_msg,
                src_msg,
                forward_func,
                log_msg,
                is_media_group,
            )
        if success:
            link = clean_link(new_msg.link)
            if edited:
                text = f'updated message {link}'
            elif deleted:
                text = f'marked message as deleted {link}'
            else:
                text = f'reposted message {link}'
            new_log_msg = log_msg.reply(
                text = text,
                quote = True,
            )
        recursive_repost(
            src_msg = new_msg,
            orig = orig,
            targets = next_chats_tree,
            log_msg = new_log_msg,
            src_link = src_link,
            edited = edited,
            deleted = deleted,
            msg_text = msg_text,
        )


def get_msg_link(
    msg: types.Message,
) -> str | None:
    if (
        not msg.link
    ) or (
        msg.link[15] == '-'
    ):
        return None
    else:
        return clean_link(msg.link)


def get_media_group(
    msg: types.Message
) -> None:
    local_dict = {
        'msgs': []
    }
    temp_data.media_groups[
        msg.media_group_id
    ] = local_dict
    chat_link = temp_data.links[msg.chat.id]
    msg_link = get_msg_link(msg)
    if msg_link:
        text = f'got media group `{msg.media_group_id}` in {msg_link}'
    else:
        text = f'got media group `{msg.media_group_id}` in {chat_link}'

    local_dict['log_msg'] = bot.send_message(
        text=text,
        chat_id=temp_data.logs_chat.id,
    )

    local_media_group = msg.get_media_group()
    for sub_msg in local_media_group:
        local_dict['msgs'].append(
            clean_link(sub_msg.link)
        )

    local_dict['count'] = len(
        local_dict['msgs']
    )

    for __media_group__ in temp_data.media_groups.values():
        local_dict['log_msg'].reply(
            text=yml.to_str(__media_group__['msgs']),
            quote=True,
        )
    return local_dict['log_msg']


def clean_media_group(
    msg
) -> None:
    msg_link = get_msg_link(msg)
    local_dict = temp_data.media_groups[msg.media_group_id]
    if msg_link in local_dict['msgs']:
        local_dict['msgs'].remove(
            clean_link(msg.link),
        )
        local_dict['log_msg'].reply(
            text=f'''
got \
{local_dict["count"] - len(local_dict['msgs'])}\
/\
{local_dict["count"]}
''',
            quote=True
        )
    else:
        local_dict['log_msg'].reply(
            text=f'''
error:
{clean_link(msg.link)} not in
{yml.to_str(local_dict['msgs'])}
''',
            quote=True
        )
    if not local_dict['msgs']:
        excluded = temp_data.media_groups.pop(
            msg.media_group_id,
            None
        )
        if not excluded:
            local_dict['log_msg'].reply(
                text=f'''
error:
{msg.media_group_id} not in
{yml.to_str(temp_data.media_groups)}
'''
            )


def resend_media_group(
    src_media: list[types.Message],
    target: int,
    log_msg: types.Message,
) -> list[types.Message]:
    msg: types.Message = None
    new_media = []
    other_captions = []
    for msg in src_media:
        if msg.caption:
            captions = list(
                text_wrap(
                    msg.caption
                )
            )
            first_caption = captions[0]
            other_captions += captions[1:]
        else:
            first_caption = None

        kwargs = {
            'msg': msg,
            'log_msg': log_msg,
        }
        if msg.photo:
            temp_msg: types.Message = resend_file(
                **kwargs,
                file=msg.photo,
                send_method=log_msg.reply_photo,
            )
            new_media.append(
                types.InputMediaPhoto(
                    media=temp_msg.photo.file_id,
                    caption=first_caption,
                )
            )
        elif msg.video:
            temp_msg: types.Message = resend_file(
                **kwargs,
                file=msg.video,
                send_method=log_msg.reply_video,
            )
            new_media.append(
                types.InputMediaVideo(
                    media=temp_msg.video.file_id,
                    caption=first_caption,
                )
            )
        elif msg.audio:
            temp_msg: types.Message = resend_file(
                **kwargs,
                file=msg.audio,
                send_method=log_msg.reply_audio,
            )
            new_media.append(
                types.InputMediaAudio(
                    media=temp_msg.audio.file_id,
                    caption=first_caption,
                )
            )
        elif msg.document:
            temp_msg: types.Message = resend_file(
                **kwargs,
                file=msg.document,
                send_method=log_msg.reply_document,
            )
            new_media.append(
                types.InputMediaDocument(
                    media=temp_msg.document.file_id,
                    caption=first_caption,
                )
            )
    return bot.send_media_group(
        chat_id=target,
        media=new_media,
    )[0]


def forward_media_group(
    msg: types.Message,
    target: int,
    reply_to_msg=None,
    log_msg=None
) -> list[types.Message]:
    return bot.copy_media_group(
        chat_id=target,
        from_chat_id=msg.chat.id,
        message_id=msg.id,
        reply_to_message_id=reply_to_msg,
    )[0]


def init_recursive_repost(
    _,
    src_msg: types.Message,
    deleted = False,
    force = False,
) -> None:
    print(src_msg)
    try:
        if isinstance(
            src_msg,
            list,
        ):
            for msg in src_msg:
                init_recursive_repost(
                    None,
                    msg,
                    deleted=True,
                )
            return
        stream = False
        if src_msg.service:
            if src_msg.service == pg.enums.MessageServiceType.VIDEO_CHAT_STARTED:
                stream = True
            else:
                return
        targets: list = temp_data.chats_tree[src_msg.chat.id]
        src_link = temp_data.links[src_msg.chat.id]
        msg_link = get_msg_link(src_msg)
        if force:
            edited = False
        else:
            edited = bool(src_msg.edit_date)

        if src_msg.caption:
            text_hash = get_hash(str(src_msg.caption))
        else:
            text_hash = get_hash(str(src_msg.text))

        if deleted:
            time.sleep(4)
            if (
                src_msg.chat.id not in history
            ) or (
                src_msg.id not in history[src_msg.chat.id]
            ):
                bot.send_message(
                    chat_id=temp_data.logs_chat.id,
                    text=f'{clean_link(src_msg.link)} message deleted but was not reposted and was not saved in `{history_path}`',
                )
                return

        if edited:
            time.sleep(4)
            if (
                src_msg.chat.id not in history
            ) or (
                src_msg.id not in history[src_msg.chat.id]
            ):
                bot.send_message(
                    chat_id=temp_data.logs_chat.id,
                    text=f'{clean_link(src_msg.link)} edited but was not reposted and was not saved in `{history_path}`',
                )
                return

            if (
                history[src_msg.chat.id][src_msg.id][
                    'text_hash'
                ] == text_hash
            ) and (
                not force
            ):
                return

            if src_msg.media_group_id:
                for msg in src_msg.get_media_group():
                    history[src_msg.chat.id][msg.id][
                        'edited_times'
                    ] += 1
            else:
                history[src_msg.chat.id][src_msg.id][
                    'edited_times'
                ] += 1
            history[src_msg.chat.id][src_msg.id][
                'text_hash'
            ] = text_hash
        else:
            if src_msg.chat.id not in history:
                history[src_msg.chat.id] = {}
            if src_msg.id not in history[src_msg.chat.id]:
                history[src_msg.chat.id][src_msg.id] = {
                    'edited_times': 1,
                    'text_hash': text_hash,
                }
        while len(history[src_msg.chat.id]) > 100:
            history[src_msg.chat.id].pop(
                min(history[src_msg.chat.id].keys()),
                None,
            )
        history.to_file()
        if edited:
            if msg_link:
                text = f'got edited message {msg_link}'
            else:
                text = f'got edited message id={src_msg.id} in {src_link}'
        elif deleted:
            text = f'got deleted message {src_msg.link}'
        else:
            if msg_link:
                text = f'got message {msg_link}'
            else:
                text = f'got message id={src_msg.id} in {src_link}'
        log(text)
        if stream:
            log_msg = bot.send_message(
                chat_id = temp_data.logs_chat.id,
                text = text
            )
            recursive_repost(
                src_msg = src_msg,
                orig = src_msg,
                targets = targets,
                log_msg = log_msg,
                src_link = src_link,
                edited = edited,
                deleted = deleted,
                msg_text = 'stream started',
            )
            chat: types.Chat = None
            for i in range(config['repeat_notifications']):
                for chat in temp_data['stream_notifications']:
                    bot.send_message(
                        chat_id = chat.id,
                        text = f'[{i + 1}/{config.repeat_notifications}] stream started',
                    )
                    time.sleep(
                        config['notifications_delay']
                    )

        elif edited or not src_msg.media_group_id:
            log_msg = bot.send_message(
                chat_id=temp_data.logs_chat.id,
                text=text
            )
            recursive_repost(
                src_msg=src_msg,
                orig=src_msg,
                targets=targets,
                log_msg=log_msg,
                src_link=src_link,
                edited=edited,
                deleted=deleted,
            )
        else:
            if src_msg.media_group_id not in temp_data.media_groups:
                log_msg = get_media_group(src_msg)
                recursive_repost(
                    src_msg=src_msg,
                    orig=src_msg,
                    targets=targets,
                    log_msg=log_msg,
                    src_link=src_link,
                    edited=edited,
                    deleted=deleted,
                )
            time.sleep(2)
            clean_media_group(src_msg)
    except Exception:
        error_path = f'{proj_path}/error.txt'
        with open(
            error_path,
            'w',
        ) as file:
            c_error = rich.console.Console(
                width=80,
                file=file,
            )
            c_error.print_exception(
                show_locals=True
            )
        c.print_exception(
            show_locals=True
        )
        c_log.print_exception(
            show_locals=True
        )
        bot.send_document(
            chat_id=temp_data.logs_chat.id,
            document=error_path,
        )


def clean_link(
    link: str,
) -> str:
    if not link:
        return
    return str(
        link.replace(
            'https://',
            '',
        ).replace(
            'http://',
            '',
        )
    )


def get_chats_from_links(
    local_chats_tree: dict
) -> list[dict]:
    if not local_chats_tree:
        return {}
    answer = []
    for source, target in local_chats_tree.items():
        answer.append(
            {
                'link': source,
                'chat': get_chat_from_link(source),
                'next_chats_tree': get_chats_from_links(target),
            }
        )
    return answer


def refresh_reposter_handlers() -> None:
    for handler in temp_data.reposter_handlers:
        bot.remove_handler(*handler)
    temp_data['reposter_handlers'] = []
    temp_data['chats_tree'] = {}
    temp_data['links'] = {}

    for src_link, targets in config.chats_tree.items():
        src_chat = get_chat_from_link(src_link)
        temp_data.chats_tree[src_chat.id] = get_chats_from_links(targets)
        temp_data.links[src_chat.id] = src_link

        for Handler in (
            MessageHandler,
            EditedMessageHandler,
            DeletedMessagesHandler,
        ):
            temp_data.reposter_handlers.append(
                bot.add_handler(
                    Handler(
                        init_recursive_repost,
                        filters=filters.chat(
                            src_chat.id
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
                    filters=blank_filter(
                        commands=commands
                    )
                )
            )
        )

    for func, commands in {
        help:
            ['help', 'h'],
        set_repeat_notifications:
            'set_repeat_notifications',
        set_stream_notifications:
            'set_stream_notifications',
        remove_stream_notifications:
            'remove_stream_notifications',
        set_can_configure_all_members_of_this_chat:
            'set_can_configure_all_members_of_this_chat',
        set_can_configure_only_me:
            'set_can_configure_only_me',
        set_save_edited_messages_history:
            'save_edited_messages_history',
        set_do_not_save_edited_messages_history:
            'do_not_save_edited_messages_history',
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
        repost_specified:
            'repost',
    }.items():
        new_handler(
            func=func,
            commands=commands,
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

    except errors.exceptions.bad_request_400.UserNotParticipant:
        bot.add_chat_members(
            chat_id=logs_chat.id,
            user_ids='gmanka_bot',
            forward_limit=0,
        )
        bot.send_message(
            text='invited @gmanka_bot just for make commands like /help clickable, he is not needed for anything else',
            chat_id=logs_chat.id,
        )
    bot.send_message(
        text=start_message + '\n\nuse /help to configure reposter',
        chat_id=logs_chat.id,
    )
    refresh_config_handlers()
    refresh_reposter_handlers()
    refresh_stream_notifications()


def update_app(
    forced = False
):
    if not config.check_updates:
        return
    if not forced:
        print('[deep_sky_blue1]checking for updates')
        with rich.progress.Progress(
            transient = True
        ) as progr:
            progr.add_task(
                total = None,
                description = ''
            )
            packages = []
            pip_list = f'{pip} list --format=json --path {modules_path}'
            all_packages_str = run(pip_list)
            start = all_packages_str.find('[')
            end = all_packages_str.rfind(']') + 1
            all_packages_str = all_packages_str[start:end]
            try:
                all_packages = json.loads(
                    all_packages_str
                )
            except json.JSONDecodeError:
                progr.stop()
                print(
                    f'''
    {pip_list} command returned non-json output:

    {all_packages_str}
    '''
                )
                return
            for package in all_packages:
                if package['name'] != app_name:
                    packages.append(
                        package['name']
                    )

            command = f'{pip} list --outdated --format=json --path {modules_path}'
            for package in packages:
                command += f' --exclude {package}'

            updates_found_str = run(command)
            updates_found = app_name in updates_found_str
            progr.stop()

        if not updates_found:
            print('updates not found')
            return
    if not forced:
        bot.send_message(
            chat_id=temp_data.logs_chat.id,
            text='''\
    please open console to update app
    changelog - github.com/gmankab/reposter/blob/main/changelog.md
    ''',
        )
        if yes_or_no.choose(
            text=f'''\
    [green]found updates, do you want to update {app_name}?
    changelog - https://github.com/gmankab/reposter/blob/main/changelog.md
    '''
        ) == 'no':
            return

    requirements = "betterdata easyselect gmanka_yml pyrogram tgcrypto humanize rich"

    match os_name:
        case 'Linux':
            update = f'''\
kill -2 {os.getpid()} && \
sleep 1 && \
{pip} install --upgrade --no-cache-dir --force-reinstall {app_name} {requirements} \
--no-warn-script-location -t {modules_path} && \
sleep 1 && \
{sys.executable} {proj_path}\
'''
        case 'Windows':
            update = f'''\
taskkill /f /pid {os.getpid()} && \
timeout /t 1 && \
{pip} install --upgrade --no-cache-dir --force-reinstall {app_name} {requirements} \
--no-warn-script-location -t {modules_path} && \
timeout /t 1 && \
{sys.executable} {proj_path}\
'''
    print(f'restarting and updating {app_name} with command:\n{update}')
    os.system(
        update
    )

def restart():
    match os_name:
        case 'Linux':
            update = f'''\
kill -2 {os.getpid()} && \
sleep 1 && \
{sys.executable} {proj_path}\
'''
        case 'Windows':
            update = f'''\
taskkill /f /pid {os.getpid()} && \
timeout /t 1 && \
{sys.executable} {proj_path}\
'''
    print(f'restarting and updating {app_name} with command:\n{update}')
    os.system(
        update
    )

def main() -> None:
    global c_log
    global print
    global log
    global bot
    init_config()
    if config['tg_session']:
        bot = pg.client.Client(
            name=app_name,
            session_string=config.tg_session,
        )
        first_start = False
    else:
        phone_number = str(config.phone_number)
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        bot = pg.client.Client(
            name=app_name,
            api_id=config.api_id,
            api_hash=config.api_hash,
            phone_number=phone_number,
            app_version=app_full_name,
            device_model=os.getlogin(),
            system_version=os_name,
            in_memory=True,
            workers=1,
        )
        first_start = True
    try:
        with bot:
            temp_data['me'] = bot.get_chat('me')
            if first_start:
                config['tg_session'] = bot.export_session_string()
            if not config['logs_chat']:
                print(
                    f'\n[bold green]please open telegram and see your "saved messages" chat - [/bold green][bold]{self_username()}')

                bot.send_message(
                    chat_id='me',
                    disable_web_page_preview=True,
                    text=f'''\
{start_message}

Please create new empty group chat and send here clickable link to it. This chat needed for logs and for configuring reposter. You must be an owner, and nobody except you must have access to this chat.

{acceptable_link_formats}
'''
                )

                temp_data.config_handlers.append(
                    bot.add_handler(
                        MessageHandler(
                            init_set_logs_chat,
                            filters=filters.chat('me'),
                        )
                    )

                )
            else:
                print(
                    f'\n[bold green]please open telegram and see your logs chat - [/bold green][bold]https://{config.logs_chat.replace("@", "t.me/")}')
                init_handlers()
                if log_path.exists() and log_path.stat().st_size:
                    bot.send_document(
                        document=log_path,
                        chat_id=temp_data.logs_chat.id,
                    )
                    log_path.unlink()

            update_app()
            with open(
                log_path,
                'a'
            ) as log_file:
                c_log = rich.console.Console(
                    file=log_file,
                    width=80,
                )

                def new_print(*args, **kwargs):
                    c.print(*args, **kwargs)
                    c_log.print(*args, **kwargs)

                def new_log(*args, **kwargs):
                    c.log(*args, **kwargs)
                    c_log.log(*args, **kwargs)

                print = new_print
                log = new_log

                pg.idle()
    except errors.AuthKeyUnregistered:
        config['tg_session'] = None
        main()


main()
