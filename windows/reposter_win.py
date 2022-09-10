from urllib import request as r
from pathlib import Path
import shutil as sh
import subprocess
import sys
import os

proj_name = 'reposter'
proj_path = Path(__file__).parent.resolve()
run_st = subprocess.getstatusoutput
print(sys.path)

try:
    import reposter
except ImportError as error_text:
    print(error_text)
    print(sys.path)

    def run(
        command: str
    ) -> str:
        return run_st(
            command
        )[-1]

    downloading_progress = 0

    def progress(
        block_num,
        block_size,
        total_size,
    ):
        global downloading_progress
        new_progress = round(
            block_num * block_size / total_size * 100
        )
        if new_progress != downloading_progress:
            downloading_progress = new_progress
            print(
                f'\r{new_progress}%',
                end = '',
            )

    pip = f'{sys.executable} -m pip'
    upgrade_pip = run(f'{pip} install --upgrade pip --no-cache-dir')

    if 'No module named pip' in upgrade_pip:
        print('downloading pip')
        # pip is a shit which allow to install libs, so if we want to install libs we must have pip
        py_dir = Path(sys.executable).parent

        # fixing shit which doesn't allow to install pip in python embeddable on windows:
        for file in os.listdir(
            py_dir
        ):
            if file[-5:] == '._pth':
                with open(
                    f'{py_dir}/{file}', 'w'
                ) as file:
                    file.write(
                        '''\
python310.zip
./../
.

import site
'''
                    )

        # downloading pip
        get_pip = f'{proj_path}/get-pip.py'
        get_pip_tmp = f'{proj_path}/get-pip.tmp'
        r.urlretrieve(
            url = 'https://bootstrap.pypa.io/get-pip.py',
            filename = get_pip_tmp,
            reporthook = progress,
        )
        print()
        Path(get_pip_tmp).rename(get_pip)

        print('Preparing to update pip')
        os.system(
            f'{sys.executable} {get_pip} --no-warn-script-location --no-cache-dir'
        )
        os.remove(get_pip)
    else:
        print(upgrade_pip)

    os.system(f'{pip} install --upgrade {proj_name} -t {proj_path} --no-cache-dir')

    restart_script = f'''\
taskkill /f /pid {os.getpid()} && \
timeout /t 1 && \
{sys.executable} {" ".join(sys.argv)}\
'''
    print(f'restarting script with command:\n{restart_script}')
    os.system(
        restart_script
    )
