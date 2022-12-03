# license: gnu gpl 3 https://gnu.org/licenses/gpl-3.0.en.html
# sources: https://github.com/gmankab/reposter

from pathlib import Path
from easyselect import Sel
import shutil as sh
import subprocess as sp
import platform
import rich
import sys
import os

app_version = '22.4.0'
app_name = 'reposter'
proj_path = Path(__file__).parent.resolve()
modules_path = Path(__file__).parent.parent.resolve()
c = rich.console.Console()
print = c.print
win_py_file = Path(f'{modules_path}/{app_name}_win.py')
portable = win_py_file.exists()
run_st = sp.getstatusoutput
run = sp.getoutput
os_name = platform.system()
yes_or_no = Sel(
    items = [
        'yes',
        'no',
    ],
    styles = [
        'green',
        'red',
    ]
)


def main():
    match os_name:
        case 'Linux':
            linux()
        case 'Windows':
            windows()


def linux():
    home = Path.home()
    share = f'{home}/.local/share'

    dotdesktop_path = Path(
        f'{home}/.local/share/applications/{app_name}.desktop'
    )
    if dotdesktop_path.exists():
        return
    dotdesktop_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    with open(
        dotdesktop_path,
        'w',
    ) as dotdesktop:
        dotdesktop.write(
f'''\
[Desktop Entry]
Comment={app_name} for telegram
Type=Application
Icon={app_name}
Name={app_name}
Terminal=true
TerminalOptions=\\s--noclose
Hidden=false
Keywords={app_name};repost;telegram
Exec=/bin/python -m {app_name}
'''
        )

    icon_source = Path(f'{proj_path}/icons/icon.svg')
    icon_target = Path(f'{share}/icons/{app_name}.svg')
    icon_target.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    sh.copy(
        icon_source,
        icon_target,
    )

    act = yes_or_no.choose(
f'''
[green]\
Created file [deep_sky_blue1]{dotdesktop_path}

[green]\
This script can be runned with following command:
[deep_sky_blue1]\
python -m {app_name}
[/deep_sky_blue1]\
Do you want do create shortcut in \
[deep_sky_blue1]/bin[/deep_sky_blue1]?
Then you will be able to run this script with [deep_sky_blue1]{app_name}[/deep_sky_blue1] command
Creating this shortcut requires sudo\
'''
    )
    match act:
        case 'yes':
            pass
        case 'no':
            return
        case 'exit':
            sys.exit()
    script = f'''\
#!/bin/bash
python -m {app_name} $@
'''
    os.system(
f'''
echo "{script}" | sudo tee /bin/{app_name}
sudo chmod +x /bin/{app_name}
'''
    )


def windows():
    shortcut = Path(
        f'{proj_path.parent.resolve()}/{proj_path.name}.lnk'
    )

    if shortcut.exists():
        return

    icon_source = Path(
        f'{proj_path}/icons/icon.ico'
    )

    home = os.environ["USERPROFILE"]

    desktop = Path(
        f'{home}/desktop/{shortcut.name}'
    )

    start_menu = Path(
        f"{home}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/gmanka/{shortcut.name}"
    )

    start_menu.parent.mkdir(
        parents = True,
        exist_ok = True,
    )

    shortcut_creator_path = f'{proj_path}/shortcut_creator.vbs'

    with open(
        shortcut_creator_path,
        'w'
    ) as shortcut_creator:
        shortcut_creator.write(
f'''\
set WshShell = WScript.CreateObject("WScript.Shell")
set Shortcut = WshShell.CreateShortcut("{shortcut}")
Shortcut.TargetPath = "{sys.executable}"
Shortcut.Arguments = "{proj_path}"
Shortcut.IconLocation = "{icon_source}"
Shortcut.Save
'''
        )
    shortcut_creator.close()
    os.system(shortcut_creator_path)
    os.remove(shortcut_creator_path)
    sh.copyfile(shortcut, desktop,)
    sh.copyfile(shortcut, start_menu)
    text = f'''
[green]\
Created shortcuts on desktop and start panel

This script can be runned with following commands:
[deep_sky_blue1]\
{sys.executable} {proj_path}
{shortcut}
{desktop}
'''
    if not portable:
        text += f'{sys.executable} -m {app_name}\n'
    print(
        text,
        highlight=False,
    )


main()
