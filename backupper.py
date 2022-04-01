'''
script to backup
python 3.10.4
'''

# importing libraries
from urllib import request as r
from inspect import cleandoc as cd
import subprocess
import pathlib
import shutil
import sys
import os


def clean_path(path):
    path = str(path).replace('\\', '/')
    # conerting a\\b///\\\c\\/d/e/ to a//b//////c///d/e/

    # conerting a//b//////c///d/e/ to a/b/c/d/e/
    while '//' in path:
        path = path.replace('//', '/')
    return path


def get_parrent_dir(file):
    return clean_path(
        pathlib.Path(file).parent
    )


def clear_dir(dir):
    shutil.rmtree(
        dir,
        ignore_errors=True,
    )

    if not os.path.isdir(downloads):
        os.mkdir(downloads)


# getting Current Work Dir path
cwd = get_parrent_dir(__file__)

# adding libs and files from Current Work Dir to sys.path
# this is needed so that python can find this libs and files, then use them

downloads = f'{cwd}/downloads'
libs = f'{cwd}/libs'

sys.path += (
    cwd,
    libs,
)
if len(sys.argv) > 1:
    config_path = sys.argv[1]
    if config_path[:2] == './':
        config_path = f'{cwd}/{config_path[2:]}'
else:
    config_path = f'{cwd}/config.yml'


def install_libs():
    print('checking libs')
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
    except ImportError as error:
        print(error)
        # clearing pip chache
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
        os.system(f'{sys.executable} {pathlib.Path(__file__)}')
        sys.exit()


install_libs()


import pyrogram
import ruamel.yaml

# this lib needed for beautiful output:
import rich
from rich import pretty


pretty.install()
print = rich.console.Console().print
yml = ruamel.yaml.YAML()


if not os.path.isfile(config_path):
    open(config_path, 'w').close()


config = yml.load(
    open(config_path, 'r')
) or {}  # empty dict if config file empty


def make_config():
    if os.stat(config_path).st_size == 0:
        # if config file empty
        created_new_config = True
        print(f'creating new config `{config_path}`')
    else:
        created_new_config = False
        print(f'loading config `{config_path}`')

    if (
        'api_id' not in config
    ) or (
        'api_hash' not in config
    ):
        print(
            '\nplease open https://my.telegram.org/apps and copy api_id and api_hash.\n[bold red]warning[/bold red]: use ony your own api_id and api_hash. I already tried to take them from decompiled official telegram app, and 20 minutes later my telegram account get banned. Then I wrote email with explanation on recover@telegram.org on the next day and they unbanned me. So please use only your own api_id and api_hash\n',
        )
        created_new_config = True

    for i in [
        'api_id',
        'api_hash',
    ]:
        if i not in config:
            config[i] = input(
                f'input {i}>> '
            )

    if 'source_chat' not in config or 'target_chat' not in config:
        open(config_path, 'w').write(
            '\nYou can find ID of any chat in your browser\'s address bar at https://web.telegram.org/z/. It must be number without letters.\n[bold red]warning[/bold red]: if ID have "-" sign at the beginning then you must add "100" after "-". For example, you must use "-100154636" instead of "-154636". Also if it hasn\'t "-" sign then you don\'t need to touch it. For example, it can be "38523532", "1348592", or "-100954843". If you want to use your account\'s "saved messages", input "me". Or you can use @name, of any user, chanel or chat.\n'
        )
        created_new_config = True

    if 'source_chat' not in config:
        config['source_chat'] = input(
            'Input id of chat which you want to backup (source chat) >> '
        )

    if 'target_chat' not in config:
        config['target_chat'] = input(
            'Input id of chat where the messages will be saved (target chat) >> '
        )

    if 'message_id_start_from' not in config:
        config['message_id_start_from'] = input(
            'input the id of the message from which to start the backupping. To backup whole chat enter 0 >> '
        )
        created_new_config = True

    if 'update_message_id_start_from' not in config:
        config['update_message_id_start_from'] = 'true'
        created_new_config = True

    if 'count_of_messages_to_backup' not in config:
        config['count_of_messages_to_backup'] = input(
            'Input count of messag es to backup. Leave blank to backup 10 messages, or input "all" to backup all messages >> '
        )
        created_new_config = True

    if not config['count_of_messages_to_backup']:
        config['count_of_messages_to_backup'] = 10
        created_new_config = True

    if not config['bugreport_chat']:
        config['bugreport_chat'] = 'me'
        created_new_config = True

    if created_new_config:
        open(config_path, 'w').write(cd(
        f"""
        # please open https://my.telegram.org/apps and copy api_id and api_hash.
        # WARNING: use ony your own api_id and api_hash. I already tried to take them from decompiled official telegram app, and 20 minutes later my telegram account get banned. Then I wrote email with explanation on recover@telegram.org on the next day and they unbanned me. So please use only your own api_id and api_hash
        api_id: {config['api_id']}
        api_hash: {config['api_hash']}

        # You can find ID of any chat in your browser's address bar at https://web.telegram.org/z/. It must be number without letters.
        # WARNING: if ID have "-" sign at the beginning then you must add "100" after "-". For example, you must use "-100154636" instead of "-154636". Also if it hasn't "-" sign then you don't need to touch it. For example, it can be "38523532", "1348592", or "-100954843". If you want to use your account's "saved messages", input "me". Or you can use @name, of any user, chanel or chat.

        # id of chat which you want to backup
        source_chat: {config['source_chat']}

        # id of chat where the messages will be saved
        target_chat: {config['target_chat']}

        # input the id of the message from which to start the backupping. To backup whole chat enter 0
        message_id_start_from: {config['message_id_start_from']}

        # if true then value of "message_id_start_from" will be updated after every backup and will be set to latest backupped message id + 1
        update_message_id_start_from: {config['update_message_id_start_from']}

        # may be a number, or "all"
        count_of_messages_to_backup: {config['count_of_messages_to_backup']}

        # chat id where bugreports will be sent
        bugreport_chat: {config['bugreport_chat']}
        """
        ))

        print(
            f'Created new config, please check it: {config_path}',
            style='bright_green'
        )

    if 'backupper.session' not in os.listdir(cwd):
        input(
            'Now you will need to log in to the account that has access to the chat that you are going to backup. Press enter to continue'
        )


make_config()

tg = pyrogram.Client(
    'backupper',
    api_id = config['api_id'],
    api_hash = config['api_hash'],
)


def show_progress(current, total):
    print(f'{current}/{total}')


def bugreport(bug):
    print(bug)
    tg.send_message(
        config['bugreport_chat'],
        bugreport,
    )


def backup(
    msg,
):
    def _backup(msg):
        # print(msg)

        media_type = msg.media
        file_id = msg[media_type].file_id

        return tg.download_media(
            file_id,
            file_name = f'{downloads}/',  # path to save file
            progress = show_progress,
        )

    clear_dir(downloads)

    if msg.media_group_id:
        files = []
        for i in tg.get_media_group(
            msg.chat.id, msg.message_id
        ):
            files.append(
                getattr(
                    pyrogram.types,
                    f'InputMedia{msg.media.title()}')(
                    _backup(i)
                )
            )
        tg.send_media_group(
            'me',
            files
        )
    else:
        _backup(msg)

    # target = config['target_chat']
    # print(msg)
    # if msg.service:
    #     return
    # if msg.text:
    #     tg.send_message(
    #         target,
    #         msg.text,
    #     )

    # if msg.caption:
    #     tg.send_message(
    #         target,
    #         msg.caption,
    #     )

    # if msg.media:
    #     if msg.document:
    #         print('downloading document')
    #         path = save(msg)
    #         print(f'uploading "{path}"')
    #         tg.send_document(
    #             target,
    #             document = path,
    #             progress = show_progress,
    #         )
    #         os.remove(path)
    #     if msg.photo:
    #         print('downloading photo')
    #         path = save(msg)
    #         print(f'uploading "{path}"')
    #         tg.send_photo(
    #             target,
    #             photo=path,
    #             progress = show_progress,
    #         )
    #         os.remove(path)

    #     if msg.voice:
    #         print('downloading voice')
    #         path = save(msg)
    #         print(f'uploading "{path}"')
    #         tg.send_voice(
    #             target,
    #             path,
    #             progress = show_progress,
    #         )
    #         os.remove(path)

    #     if msg.audio:
    #         print('downloading audio')
    #         path = save(msg)
    #         print(f'uploading "{path}"')
    #         tg.send_document(
    #             target,
    #             path,
    #             progress = show_progress,
    #         )
    #         os.remove(path)

    #     if msg.video:
    #         print('downloading video')
    #         path = save(msg)
    #         print(f'uploading "{path}"')
    #         tg.send_video(
    #             target,
    #             path,
    #             progress = show_progress,
    #         )
    #         os.remove(path)

    #     if msg.video_note:
    #         print('downloading video_note')
    #         path = save(msg)
    #         print(f'uploading "{path}"')
    #         tg.send_video_note(
    #             target,
    #             path,
    #             progress = show_progress,
    #         )
    #         os.remove(path)


def main():
    clear_dir(downloads)

    limit = config['count_of_messages_to_backup']
    if limit == 'all':
        limit = None
    else:
        limit = int(limit)

    with tg:
        print(
            '\ngetting messages',
            f'chat_id = {config["source_chat"]}',
            f'limit = {limit}',
            f'offset_id = {config["message_id_start_from"]}',
            f'reverse = {True}',
            sep = '\n'
        )

        for msg in tg.iter_history(
            chat_id = config['source_chat'],
            limit = limit,
            offset_id = int(config['message_id_start_from']),
            reverse = True,
        ):
            backup(msg)

            latest = msg.message_id

    if config['update_message_id_start_from']:
        config['message_id_start_from'] = latest

    clear_dir(downloads)


main()
