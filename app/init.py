from urllib import request as r
from inspect import cleandoc as cd
from pathlib import Path
from collections.abc import Iterable
import func as f
import subprocess
import sys
import os


def config_create(
    latest_supported_config,
    script_version,
):
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


# kill all python instances before starting bot
kill_python: false
# sometimes bot ignoring messages if this option is set to false


# # # WARNING: DON'T TOUCH VERSION
# # # WARNING: DON'T TOUCH VERSION
version: {script_version}  # # # WARNING: DON'T TOUCH VERSION
# # # WARNING: DON'T TOUCH VERSION
# # # WARNING: DON'T TOUCH VERSION
"""

    def new():
        config = config_load(blank_config)
        config_dump(config)
        c.print(f'Created new config: {config_path}, please check, read and fill it. You can close this script for now and open it later, after filling config. Or don\'t close it and just press Enter after filling config to continue', style = 'light_green')
        input()
        config_load()

    if (
        Path(config_path).exists()
    ) and (
        os.stat(config_path).st_size != 0
    ):
        config = config_load()
        if latest_supported_config and script_version:
            if (
                'version' not in config
            ) or (
                str(config['version']) < latest_supported_config
            ) or (
                str(config['version']) > script_version
            ):
                c.print(f'[red]old[/red] {config_path} [red]file renamed to[/red] {f.auto_rename(config_path)}')
                new()
    else:
        new()

    def recursive_check(dict = config):
        while '_' in dict.values():
            for key, val in dict.items():
                if isinstance(val, Iterable) and not isinstance(val, str):
                    for i in val:
                        recursive_check(i)
                if val == '_':
                    c.print(
                        f'[bright_red]please specify value for[/bright_red] {key} [bright_red]in config'
                    )
            c.print(f'your config path - [purple]{config_path}')
            input('press enter to continue')
            config_load()
    recursive_check()
    if config['kill_python']:
        pass
    return config


def install_libs():
    print('installing libs')
    requirements = [
        'rich',
        'tgcrypto',
        'pyrogram',
        'ruamel.yaml',
    ]

    pip = f'{sys.executable} -m pip'
    pip_chache = f'{downloads}/pip_chache'
    output = subprocess.getstatusoutput(
        f'{pip} install --upgrade pip'
    )[1]
    print(output)
    if 'No module named pip' in output:
        print('installing pip...')
        # pip is a shit which allow to install libs, so if we want to install libs we must have pip
        py_dir = f.parrent(sys.executable)

        # fixing shit which doesn't allow to install pip in python embeddable in windows:
        for file in os.listdir(
            py_dir
        ):
            if file[-5:] == '._pth':
                with open(
                    f'{py_dir}/{file}', 'r+'
                ) as file:
                    if '#import site' in file.readlines()[-1]:
                        file.write('import site')

        # installing pip:
        get_pip = f'{downloads}/get-pip.py'
        f.mkdir(downloads)

        r.urlretrieve(
            url = 'https://bootstrap.pypa.io/get-pip.py',
            filename = get_pip,
        )
        os.system(f'{sys.executable} {get_pip} --no-warn-script-location')
        os.remove(get_pip)

    if Path(libs_dir).exists():
        print(f'deleting {libs_dir}')
        # f.rmtree(libs_dir)
    os.system(f'{pip} config set global.no-warn-script-location true')
    os.system(f'{pip} install -U {" ".join(requirements)} -t {libs_dir} --cache-dir {pip_chache}')


def config_load(
    data = None
):
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
    return config


def config_dump(
    data
):
    yml.dump(
        data,
        open(
            config_path,
            'w',
        ),
    )


proj_root  = f'{f.parrent(__file__, 2)}'
app_dir = f'{proj_root}/app'
libs_dir = f'{app_dir}/libs'
data_dir = f'{proj_root}/data'
config_path = f'{data_dir}/config.yml'
downloads = f'{data_dir}/downloads'

f.mkdir(data_dir)


try:
    from libs.ruamel import yaml  # type: ignore
    from libs.rich import pretty, console  # type: ignore
except ImportError as import_error:
    print(import_error)
    install_libs()
    print('restarting')
    f.restart()


pretty.install()
yml = yaml.YAML()
c = console.Console(
    record = True
)
