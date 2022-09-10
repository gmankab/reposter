@echo off

set cwd=%~dp0
set proj_name=reposter
set proj_path=%cwd%\%proj_name%
set proj_py=%proj_path%\%proj_name%_win.py
set tmp_name=%proj_path%\%proj_name%_win.tmp
set project_link=https://raw.githubusercontent.com/gmankab/reposter/main/windows/reposter_win.py
set python_version=3.10.7
set python_dir=%proj_path%\.python_%python_version%
set python=%python_dir%\python.exe
set python_tmp=%python_dir%\python.tmp
set python_zip=%python_dir%\python.zip
set python_link=https://python.org/ftp/python/%python_version%/python-%python_version%-embed-amd64.zip


if not exist "%proj_path%" (
    echo %proj_name% supports only latest versions of windows 10 and 11
    echo if errors occur, please update windows
    pause
    mkdir "%proj_path%"
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


if not exist "%proj_py%" (
    echo downloading %proj_py% from "%project_link%"
    curl -SL "%project_link%" -o "%tmp_name%"
    ren "%tmp_name%" "%proj_name%_win.py"
)

"%python%" "%proj_py%" portable %*
