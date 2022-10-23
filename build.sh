#!/bin/bash

rm -r ./dist
python -m hatchling build
pip uninstall -y reposter
pip install ./dist/reposter*.whl --no-warn-script-location
cd ~ || echo 'error'
python -m reposter
