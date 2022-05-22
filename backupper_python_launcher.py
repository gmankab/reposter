import sys
import os
from pathlib import Path

def restart():
    command = f'{sys.executable} {sys.argv[0]}'
    globals().clear()
    import os as new_os
    import sys as new_sys
    new_os.system(command)
    new_sys.exit()

os.system(
    f'{sys.executable} {Path(__file__).resolve().parent}/app/backupper.py'
)
