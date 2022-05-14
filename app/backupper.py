script_version = '2.7'
relese_type = 'stable'
latest_supported_config = '2.7'
required_python = '3.10'
print('starting...')


import os
import sys
from urllib import request as r
from pathlib import Path


def check_vers():
    py_vers = sys.version.split()[0]
    if py_vers < required_python:
        raise BaseException(
            f"your python version - '{py_vers}'\nrequired - {required_python}"
        )


check_vers()


def check_update():
    def restart():
        command = f'{sys.executable} {sys.argv[0]}'
        globals().clear()
        import os as new_os
        import sys as new_sys
        new_os.system(command)
        new_sys.exit()

    def get_bytes(url):
        return r.urlopen(url).read()

    def rewrite(
        file,
        bytes,
    ):
        file = Path(file).resolve()
        print(f'updating {file}')
        open(file, 'wb').write(bytes)
        print('done')

    urls = (
        'https://raw.githubusercontent.com/gmankab/suggest/main/latest_release/init.py',
        'https://raw.githubusercontent.com/gmankab/suggest/main/latest_release/func.py',
        'https://raw.githubusercontent.com/gmankab/suggest/main/latest_release/bot.py',
    )
    main_b = get_bytes('https://raw.githubusercontent.com/gmankab/suggest/main/latest_release/suggest.py')
    main_text = main_b.decode("utf8")
    begin = main_text.find("'") + 1
    end = main_text.find("'", begin)
    new_version = main_text[begin:end]
    if new_version > script_version:
        rewrite(
            __file__,
            main_b,
        )
        for url in urls:
            filename = url.rsplit('/', 1)[-1]
            file = f'{__file__}/../{filename}'
            rewrite(
                file,
                get_bytes(
                    url
                )
            )
        print('done, restartind!')
        restart()
    for url in urls:
        filename = url.rsplit('/', 1)[-1]
        file = f'{__file__}/../{filename}'
        if not Path(file).exists():
            rewrite(
                file,
                get_bytes(
                    url
                )
            )


# check_update()

proj_root = str(Path(__file__).resolve().parent.parent)
data_dir = f'{proj_root}/data'
app_dir = f'{proj_root}/app'
libs_dir = f'{app_dir}/libs'

os.chdir(data_dir)
for dir in (
    app_dir,
    libs_dir,
    proj_root,
):
    if dir not in sys.path:
        sys.path.append(dir)

from app.init import config_create
from libs.rich import pretty

pretty.install()
config_create(
    latest_supported_config,
    script_version,
)

import bot
text = f'started bot v{script_version}'
bot.main(text)
# bot.start_bot(f'started bot v{script_version}')
