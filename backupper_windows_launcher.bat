@echo off

set cwd=%~dp0
cd "%cwd%"

set filename=backupper_python_launcher
set python_version=3.10.4
set python_dir=%cwd%python%python_version%
set python=%python_dir%\python.exe
set python_tmp=%python_dir%\python.tmp
set python_zip=%python_dir%\python.zip
set tmp_name=%cwd%\%filename%.tmp
set project_py=%cwd%\%filename%.py
set python_link=https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-amd64.zip
set project_link=https://raw.githubusercontent.com/gmankab/backupper/main/universal_python_launcher.py


if not exist "%python_dir%" (
    echo %filename% supports only latest versions of windows 10 and 11
    echo if errors occur, update windows
    pause
    mkdir "%python_dir%"
)
if not exist "%python%" (
    if not exist "%python_zip%" (
        echo downloading python %python_version%...
        curl "%python_link%" -o "%python_tmp%"
        ren "%python_tmp%" "python.zip"
    )
    echo unzipping python %python_version%...
    cd "%python_dir%"
    tar -xf "%python_zip%"
    cd "%cwd%"
)

if not exist "%project_py%" (
    echo downloading %project_py%...
    curl "%project_link%" -o "%tmp_name%"
    ren "%tmp_name%" "%filename%.py"
)

"%python%" "%project_py%" %*
