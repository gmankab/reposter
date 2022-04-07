# gmanka backupper

```text
              __
    ____ _   / /_
   / __ `/  / __ \   Gmanka
  / /_/ /  / /_/ /   Backupper
  \__, /  /_.___/    v2.6
 /____/
```

[changelog](changelog.md)

## supported OS

- windows 10, 11
- linux
- mac
- android with [termux](https://github.com/termux/termux-app/releases)
- ios with [terminus](https://apps.apple.com/ru/app/termius-terminal-ssh-client/id549039908)

## unsupported OS

- windows 8 or earlier

## usage

- easy way for windows:
  - download latest [backupper.bat](https://github.com/gmankab/backupper/releases/download/2.1/backupper.bat)
  - run it

- hard way for any OS:
  - install [python-3.10.4](https://www.python.org/downloads/release/python-3104/) ([link for windows](https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-amd64.zip))
  - download latest [backupper.py](https://raw.githubusercontent.com/gmankab/backupper/main/latest_release/backupper.py), just open link in browser and press <kbd>ctrl-s</kbd>
  - run this file using python. To run it from terminal, you must:
    - copy full path to python executable (on windows it is `python.exe`)
    - copy full path to backupper.py
    - open terminal
    - run this commands: ```path/to/python path/to/backupper.py```
