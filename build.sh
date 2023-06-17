#!/bin/bash

. .venv/bin/activate
rm -r ./dist
python -m hatchling build

