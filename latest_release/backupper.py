script_version = '2.6'
relese_type = 'stable'
latest_supported_config = '2.2'

'''
script to backup
'''

# importing libraries
from urllib import request as r
from inspect import cleandoc as cd
from pathlib import Path
import subprocess
import traceback
import textwrap
import shutil
import time
import sys
import os


def clean(path):
    path = str(path).replace('\\', '/')
    # conerting a\\b///\\\c\\/d/e/ to a//b//////c///d/e/

    # conerting a//b//////c///d/e/ to a/b/c/d/e/
    while '//' in path:
        path = path.replace('//', '/')
    return path


def get_parrent_dir(file):
    return clean(Path(file).parent)


def mkdir(dir):
    Path(dir).mkdir(
        parents=True,
        exist_ok=True
    )


def clear_dir(dir):
    shutil.rmtree(
        dir,
        ignore_errors=True,
    )
    mkdir(dir)


def restart():
    os.system(f'{sys.executable} {Path(__file__)}')
    sys.exit()


# changing current work dir
cwd = f'{get_parrent_dir(__file__)}/data'
mkdir(cwd)
os.chdir(cwd)

downloads = f'{cwd}/downloads'
libs = f'{cwd}/libs'

# adding libs and files from Current Work Dir to sys.path
# this is needed so that python can find this libs and files, then use them

sys.path += (
    cwd,
    libs,
)

if len(sys.argv) > 1:
    config_path = sys.argv[1]
else:
    config_path = f'{cwd}/config.yml'


def install_libs():
    print('checking if all libs installed...')
    pip = f'{sys.executable} -m pip'

    requirements = [
        'rich',
        'pyrogram',
        'tgcrypto',
        'ruamel.yaml'
    ]

    try:
        for requirement in requirements:
            __import__(requirement)
    except ImportError as import_error:
        print(import_error)
        print('deleating pip chache')
        output = subprocess.getstatusoutput(
            f'{pip} cache purge'
        )[1]
        print(output)
        if 'No module named pip' in output:
            print('installing pip...')
            # pip is a shit which allow to install libs, so if we want to install libs we must have pip
            py_dir = get_parrent_dir(sys.executable)

            # fixing shit which doesn't allow to install pip in python embedable in windows:
            for file in os.listdir(
                py_dir
            ):
                if file[-5:] == '._pth':
                    with open(
                        f'{py_dir}/{file}', 'r+'
                    ) as file:
                        if '#import site' in file.readlines()[-1]:
                            file.write('import site')

            # instaling pip:
            get_pip = f'{downloads}/get-pip.py'
            clear_dir(downloads)

            r.urlretrieve(
                url = 'https://bootstrap.pypa.io/get-pip.py',
                filename = get_pip,
            )
            os.system(f'{sys.executable} {get_pip} --no-warn-script-location')

        os.system(f'{pip} config set global.no-warn-script-location true')
        os.system(f'{pip} install -U pip {" ".join(requirements)} -t {libs}')
        print('installed, restarting...')
        clear_dir(downloads)
        restart()
    print('done')


install_libs()


import pyrogram
import ruamel.yaml

# this lib needed for beautiful output:
import rich
from rich import pretty


pretty.install()
yml = ruamel.yaml.YAML()
config = {}
rich_print = rich.console.Console().print
print = rich_print


if not os.path.isfile(config_path):
    open(config_path, 'w').close()


def load_config(
    data = None
):
    global config
    if data:
        config = yml.load(
            data
        ) or {}
    else:
        config = yml.load(
            open(
                config_path,
                'r'
            ).read()
        ) or {}


def dump_config(
    data = None
):
    if not data:
        data = config
    yml.dump(
        data,
        open(
            config_path,
            'w',
        ),
    )


def auto_rename(file):
    file = Path(file)
    ls = os.listdir(file.parent)
    count = 0
    new_name = file.name
    while new_name in ls:
        count += 1
        new_name = f'{file.stem}{count}{file.suffix}'
    os.rename(file, new_name)
    return clean(Path(file.parent, new_name))


def make_config():
    blank_config = f"""\
# # # please reset all "_" with your values. All values must be specified without quotes.

# # # API KEY
# # # open https://my.telegram.org/apps and copy api_id and api_hash
# # # WARNING: use ony your own api_id and api_hash. I already tried to take them from decompiled official telegram app, and 20 minutes later my telegram account get banned. Then I wrote email with explanation on recover@telegram.org and on the next day and they unbanned me.
api_id: _
api_hash: _
phone_number: _

# # # example:
# api_id: 12345
# api_hash: 0123456789abcdef0123456789abcdef
# phone_number: +12223334455


# # # CHATS ID
# # # You can find ID of any chat in your browser's address bar at https://web.telegram.org/z/. It must be number without letters.
# # # WARNING: if ID have "-" sign at the beginning then you must add "100" after "-". For example, you must use "-100154636" instead of "-154636". Also if it hasn't "-" sign then you don't need to touch it.
# # # If you want to use your account's "saved messages", input "me".
# # # Or you can use @name, of any user, chanel or chat.

# # # source chat is a chat which you want to backup
# # # target chat is a chat where the messages will be saved

chats:
- source: _
  target: _
  forward_way: _
# # # uncomment strings below if you want to backup multiple chats
# # # just delete "# " to uncomment strings
# - source: _
#   target: _
#   forward_way: _
# - source: _
#   target: _
#   forward_way: _

# # # Example 1:
# chats:
# - source: gmanka
#   target: me
#   forward_way: save_on_disk
# # # it will backup your dialogue with @gmanka to saved messages

# # # Example 2:
# chats:
# - source: 340953532
#   target: me
#   forward_way: save_on_disk
# - source: -10018483
#   target: my_cool_channel
#   forward_way: forward
# - source: durov
#   target: zelensky
#   forward_way: save_on_disk
# # # it will backup 3 chats at once. Messages from chat with id "340953532" to saved messages, messages from chat with id "-10018483" to @my_cool_channel, and messages from @durov to @zelensky. You can enter as many chats as you want, for example 10 or 100

# # # this script can send logs and bugreports in chats
log_chat:
bugreport_chat:
# # # don't touch it and leave blank if you don't want to read logs and bugreports in telegram

# # # Example 1:
# log_chat:
# bugreport_chat: me
# # # no logs, bugreports in saved messages

# # # Example 2:
# log_chat: -1001691839821
# bugreport_chat: -1001601095783
# # # logs and bugreports in specified chats


script_updates: automatic
# script_updates: disabled
# script_updates: ask


# # # WARNING: DON'T TOUCH VERSION
# # # WARNING: DON'T TOUCH VERSION
version: {script_version}  # # # WARNING: DON'T TOUCH VERSION
# # # WARNING: DON'T TOUCH VERSION
# # # WARNING: DON'T TOUCH VERSION
"""

    def new():
        load_config(blank_config)
        dump_config()
        rich_print(f'Created new config: {config_path}, please check, read and fill it. You can close this script for now and open it later, after filling config. Or don\'t close it and just press Enter after filling config to continue', style = 'light_green')
        input()
        load_config()

    if (
        Path(config_path).exists()
    ) and (
        os.stat(config_path).st_size != 0
    ):
        load_config()
        if (
            'version' not in config
        ) or (
            str(config['version']) < latest_supported_config
        ):
            rich_print(f'[red]old[/red] {config_path} [red]file renamed to[/red] {auto_rename(config_path)}')
            new()
    else:
        new()


tg = None


def print(
    *args,
    **kwargs
):
    rich_print(
        *args,
        **kwargs
    )

    if args and 'log_chat' in config:
        text = str(args[0])
        chunk_size = 1000
        for i in range(0, len(text), chunk_size):
            tg.send_message(
                config['log_chat'],
                text[i:i + chunk_size],
            )


def progress_callback(current, total):
    print(f'{current}/{total}')


def check_update():
    if config['script_updates'] == 'disabled':
        return
    url = 'https://raw.githubusercontent.com/gmankab/backupper/main/latest_release/backupper.py'
    script_b = r.urlopen(url).read()
    script = script_b.decode("utf8")
    begin = script.find("'") + 1
    end = script.find("'", begin)
    new_version = script[begin:end]
    if new_version <= script_version:
        return
    print(f'found new script version: {new_version}')
    if config['script_updates'] == 'ask':
        answer = ''
        while answer not in [
            'y',
            'n',
        ]:
            print('wanna update? y/n')
            answer = input().lower()
        if answer == 'n':
            return
    print('updating...')
    open(__file__, 'wb').write(script_b)
    print()
    print('done, restartind!')
    print()
    restart()


class Handler:
    def __init__(
        self,
        source,
        target,
        forward_way,
    ):
        self.source = source
        self.target = target
        self.latest_id = 0
        self.runned = False
        self.downloads = f'{downloads}/{self.source}/'
        if forward_way == 'save_on_disk':
            backup = self.save_on_disk
        else:
            backup = self.forward
        tg.add_handler(
            pyrogram.handlers.MessageHandler(
                callback = backup,
                filters = pyrogram.filters.chat(
                    source
                ) & ~pyrogram.filters.edited
            )
        )

    def forward(
        self,
        client,
        msg,
    ):
        print(msg)
        if msg.media_group_id:
            if msg.media_group_id > self.latest_id:
                self.latest_id = msg.media_group_id
            else:
                return
            tg.copy_media_group(
                chat_id = self.target,
                from_chat_id = msg.chat.id,
                message_id = msg.message_id,
            )
        else:
            msg.copy(
                self.target,
            )

    def save_on_disk(
        self,
        client,
        msg,
    ):
        while self.runned:
            time.sleep(1)
        self.runned = True
        clear_dir(downloads)
        print(msg)

        def download(msg, index = None):
            print()
            id = msg.message_id
            print(f'latest = {self.latest_id}')
            print(f'id = {id}')
            if id <= self.latest_id:
                print('aborted')
                return 'aborted'
            self.latest_id = id
            print(f'now latest is {self.latest_id}')
            print()

            media_type = msg.media
            file_id = msg[media_type].file_id
            print('downloading file:')
            print(f'file_id = {file_id}')
            caption = msg.caption
            print(f'caption = {caption}')
            print(f'media_type = {media_type}')
            path = Path(
                clean(
                    tg.download_media(
                        msg,
                        file_name = self.downloads,  # path to save file
                        progress = progress_callback
                    )
                )
            )
            if index is not None:
                new_path = f'{path.parent}/{index}{path.suffix}'
                os.rename(
                    path,
                    new_path,
                )
                path = new_path

            print(f'downloaded {path}')
            return (path, caption)

        if msg.media_group_id:
            print(f'found media group: {msg.media_group_id}')
            files = []
            for index, sub_msg in enumerate(
                tg.get_media_group(
                    msg.chat.id, msg.message_id
                )
            ):
                downloaded = download(sub_msg, index)
                if downloaded != 'aborted':
                    path, caption = downloaded
                    files.append(
                        getattr(
                            pyrogram.types,
                            f'InputMedia{sub_msg.media.title()}'
                        )(
                            media = path,
                            caption = caption,
                        )
                    )
            if files:
                print(
                    'sending files',
                    files,
                )
            tg.send_media_group(
                chat_id = self.target,
                media = files,
            )
            print('done.')
        elif msg.media:
            downloaded = download(msg)
            if downloaded != 'aborted':
                path, caption = downloaded
                print(
                    f'sending {msg.media} {path}'
                )
                if caption:
                    getattr(
                        tg,
                        f'send_{msg.media}',
                    )(
                        self.target,
                        path,
                        caption = caption,
                        progress = progress_callback,
                    )
                else:
                    getattr(
                        tg,
                        f'send_{msg.media}',
                    )(
                        self.target,
                        path,
                    progress = progress_callback,
                    )
        elif msg.text:
            print(f'sending text "{msg.text}"')
            tg.send_message(
                self.target,
                msg.text,
            )
        self.runned = False


def main():
    try:
        global tg
        make_config()

        phone_number = str(config['phone_number'])
        if phone_number[0] != '+':
            phone_number = '+' + phone_number

        tg = pyrogram.Client(
            'backupper',
            api_id = config['api_id'],
            api_hash = config['api_hash'],
            phone_number = phone_number,
            workdir = cwd,
        )

        handlers = []
        tg.start()

        for chat in config['chats']:
            handlers.append(
                Handler(
                    chat['source'],
                    chat['target'],
                    chat['forward_way'],
                )
            )

        check_update()

        print('start')
        pyrogram.idle()
    except:
        error = traceback.format_exc()
        print(error)

        if 'bugreport_chat' in config:
            for text in textwrap.wrap(
                str(error),
                1000,
            ):
                tg.send_message(
                    config['log_chat'],
                    text,
                )
                tg.send_message(
                    config['bugreport_chat'],
                    error,
              )


main()
