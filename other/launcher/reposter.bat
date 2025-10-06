@echo off
setlocal enabledelayedexpansion
set python_version=3.13.7
set app_name=reposter
set deps=%app_name%
set app_path=%~dp0
set data_path=%app_path%/data
set venv_bin=%data_path%/.venv/scripts
set python_link=python.org/ftp/python/%python_version%/python-%python_version%-embed-amd64.zip
set uv_link=github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip


if not exist "%data_path%" (
    mkdir "%data_path%"
)
if not exist "%data_path%/python/python.exe" (
    if not exist "%data_path%/python.zip" (
        curl -L "%python_link%" -o "%data_path%/python.zip" --insecure
    )
    mkdir "%data_path%/python"
    tar -xf "%data_path%/python.zip" -C "%data_path%/python"
)
if not exist "%data_path%/uv.exe" (
    if not exist "%data_path%/uv.zip" (
        curl -L "%uv_link%" -o "%data_path%/uv.zip" --insecure
    )
    tar -xf "%data_path%/uv.zip" -C "%data_path%"
)
if not exist "%data_path%/.venv" (
    "%data_path%/uv.exe" venv "%data_path%/.venv" "--python=%data_path%/python/python.exe"
    if /I "%big_tests%"=="true" (
        set deps=%app_name%[tests]
    )
    if /I "%tests%"=="true" (
        set deps=%app_name%[tests]
    )
    "%data_path%/uv.exe" pip install !deps! "--python=%venv_bin%/python.exe"
)

set reposter_data_dir=%data_path%
"%venv_bin%/reposter.exe"
pause
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

