'''
script to backup
'''

# importing libraries
from audioop import reverse
from operator import ge
import pathlib
import asyncio
import logging
import shutil
import sys
import os


# logging.disable(logging.CRITICAL)
# disabling annoying warnings messages


# getting Current Work Dir path
cwd = str(
    pathlib.Path(__file__).parent
).replace('\\', '/')


while '//' in cwd:
    cwd = cwd.replace('//', '/')
# conerting a\\b\\\\\\\c///d\e/ to a/b/c/d/e/


# adding libs and files from Current Work Dir to sys.path
# this is needed so that python can find this libs and files, then use them
sys.path += (
    cwd,
    f'{cwd}/libs',
    f'{cwd}/dev_libs.zip',
)


from rich import print
from rich import pretty
import pyrogram
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


def show_progress(current, total):
    print(f'{current}/{total}')


def main():
    with app:
        target = 'me'
        downloads = f'{cwd}/downloads/'

        # removing chache dir
        shutil.rmtree(
            downloads,
            ignore_errors=True,
        )

        def save(msg):  # save file and return path to it
            if not os.path.isdir(downloads):
                os.mkdir(downloads)
            app.download_media(
                msg,
                file_name = downloads,  # path to save file
                progress = show_progress,
            )
            downloaded = os.listdir(downloads)
            if downloaded:
                return downloads + downloaded[0]  # returns saved file path
            else:
                raise FileExistsError(
                    f'nothing downloaded from this message:\n{msg}'
                )

        def backup(msg):
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
                print(f'uploading {path}')
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

        print('getting messages')
        for msg in app.iter_history(
            -1001655504016,
            reverse = True
        ):
            backup(msg)


main()
