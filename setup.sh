#!/bin/bash

source ./.venv/bin/activate
apt install youtube-dl
python3 -m pip install -r ./requirements.txt