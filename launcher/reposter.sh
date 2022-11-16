#!/bin/bash

app_name="reposter"
requirements="betterdata easyselect gmanka_yml pyrogram tgcrypto humanize rich"
check_app () {
    cd "$HOME" || echo 'error'
    installed=$(python -m pip list | grep "$app_name")
    case "$installed" in
        *"$app_name"* )
            python -m "$app_name";;
        * )
            python -m pip install --upgrade --force-reinstall $app_name $requirements
            python -m "$app_name";;
    esac
}

check_pip () {
    cd "$HOME" || echo 'error'
    installed="$(sh -c 'python -m pip 2>&1')"
    case "$installed" in
        *"No module named"* )
            curl -sSL bootstrap.pypa.io/get-pip.py | python - --no-warn-script-location;
            check_app;;
        * )
            check_app;;
    esac
        
}

py="$(python --version)"
case "$py" in
    "Python"* )
        check_pip;;
    * )
        echo "python is not installed, please install it";;
esac
