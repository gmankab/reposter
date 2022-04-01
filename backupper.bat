@echo off

set cwd=%~dp0
cd "%cwd%"

set project_name=backupper
set python_version=3.10.4
set python_dir=%cwd%python%python_version%
set python=%python_dir%\python.exe
set python_tmp=%python_dir%\python.tmp
set python_zip=%python_dir%\python.zip
set project_tmp=%cwd%\%project_name%.tmp
set project_py=%cwd%\%project_name%.py
set python_link=https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-amd64.zip
set project_link=https://raw.githubusercontent.com/gmankab/backupper/main/latest_release/backupper.py


if not exist "%python_dir%" (
    echo %project_name% supports only latest versions of windows 10 and 11
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
    curl "%project_link%" -o "%project_tmp%"
    ren "%project_tmp%" "%project_name%.py"
)

"%python%" "%project_py%"
