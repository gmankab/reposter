#!/bin/bash

rm .dist/*
python -m hatchling build
pip install ./dist/reposter*.whl --force-reinstall --no-warn-script-location
cd ~ || echo 'error'
python -m reposter
