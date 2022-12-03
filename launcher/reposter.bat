@echo off

set cwd=%~dp0
set app_name=reposter
set app_path=%cwd%\%app_name%
set app_py=%app_path%\%app_name%_win.py
set tmp_name=%app_path%\%app_name%_win.tmp
set app_link=https://raw.githubusercontent.com/gmankab/%app_name%/main/launcher/%app_name%_win.py
set python_version=3.10.8
set python_dir=%app_path%\.python_%python_version%
set python=%python_dir%\python.exe
set python_tmp=%python_dir%\python.tmp
set python_zip=%python_dir%\python.zip
set python_link=https://python.org/ftp/python/%python_version%/python-%python_version%-embed-amd64.zip


if not exist "%app_path%" (
    mkdir "%app_path%"
)


if not exist "%python_dir%" (
    mkdir "%python_dir%"
)


if not exist "%python%" (
    if not exist "%python_zip%" (
        echo downloading python %python_version% from %python_link%
        curl -SL "%python_link%" -o "%python_tmp%"
        ren "%python_tmp%" "python.zip"
    )
    echo unzipping python %python_version%
    cd "%python_dir%"
    tar -xf "%python_zip%"
    cd "%cwd%"
)


if not exist "%app_py%" (
    echo downloading %app_py% from "%app_link%"
    curl -SL "%app_link%" -o "%tmp_name%"
    ren "%tmp_name%" "%app_name%_win.py"
)

"%python%" "%app_py%" %*

pause
