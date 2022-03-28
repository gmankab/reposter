'''
script to backup
'''

# importing libraries
from urllib import request as r
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


# getting Current Work Dir path
cwd = get_parrent_dir(__file__)

# adding libs and files from Current Work Dir to sys.path
# this is needed so that python can find this libs and files, then use them
sys.path += (
    cwd,
    f'{cwd}/libs',
)

downloads = f'{cwd}/downloads'


def install_libs():
    print('checking libs')
    pip = f'{sys.executable} -m pip'

    requirements = [
        'rich'
        'pyrogram'
        'tgcrypto'
        'pyyaml'
    ]

    try:
        for requirement in requirements:
            __import__(requirement)
    except ImportError:
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
                    with open(f'{py_dir}/file', 'r+') as file:
                        print(file.read())

            # instaling pip:
            get_pip = f'{downloads}/get-pip.py'
            if not os.path.isdir(downloads):
                os.mkdir(downloads)

            r.urlretrieve(
                url = 'https://bootstrap.pypa.io/get-pip.py',
                filename = f'{downloads}/get-pip.py',
            )

        # os.popen(f'{pip} install -U pip {" ".join(requirements)}')


install_libs()


import pyrogram

# this lib needed for beautiful output:
from rich import print
from rich import pretty
pretty.install()


print('starting')

if 'config.py' in os.listdir(cwd):
    from config import api_id, api_hash
else:
    api_id = ''
    api_hash = ''


app = pyrogram.Client(
    'backupper',
    api_id = api_id,
    api_hash = api_hash,
)


def clear_dir(dir):
    shutil.rmtree(
        dir,
        ignore_errors=True,
    )


def show_progress(current, total):
    print(f'{current}/{total}')


def save(
    msg,
):
    '''
    save file and return path to it
    '''
    clear_dir(downloads)

    if not os.path.isdir(downloads):
        os.mkdir(downloads)
    app.download_media(
        msg,
        file_name = downloads,  # path to save file
        progress = show_progress,
    )
    downloaded = os.listdir(downloads)
    if downloaded:
        return f'{downloads}/{downloaded[0]}'  # returns saved file path
    else:
        print(
            'nothing downloaded from this message:',
            msg,
            'please contact developer',
            sep = '\n'
        )


def backup(
    msg,
    target = 'me',
):
    print(msg)
    if msg.service:
        return
    if msg.text:
        app.send_message(
            target,
            msg.text,
        )

    if msg.caption:
        app.send_message(
            target,
            msg.caption,
        )

    if msg.document:
        print('saving document')
        path = save(msg)
        print(f'uploading "{path}"')
        app.send_document(
            target,
            document = path,
            progress = show_progress,
        )
        os.remove(path)
    if msg.media:
        if msg.photo:
            print('saving photo')
            path = save(msg)
            print(f'uploading {path}')
            app.send_photo(
                target,
                photo=path,
                progress = show_progress,
            )
            os.remove(path)

        if msg.voice:
            print('saving voice')
            path = save(msg)
            print(f'uploading {path}')
            app.send_voice(
                target,
                path,
                progress = show_progress,
            )
            os.remove(path)

        if msg.audio:
            print('saving audio')
            path = save(msg)
            print(f'uploading {path}')
            app.send_document(
                target,
                path,
                progress = show_progress,
            )
            os.remove(path)

        if msg.video:
            print('saving video')
            path = save(msg)
            print(f'uploading {path}')
            app.send_video(
                target,
                path,
                progress = show_progress,
            )
            os.remove(path)


def main():
    with app:
        print('getting messages')
        for msg in app.iter_history(
            chat_id = -1001655504016,
            limit = None,
            offset_id = 8,
            reverse = True,
        ):
            backup(msg)
            # print(msg)
    clear_dir(downloads)


main()
