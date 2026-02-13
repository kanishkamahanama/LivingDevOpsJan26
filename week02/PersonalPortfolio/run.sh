#!/bin/bash

# create a virtual environment
python3 -m venv .venv

# activate the virtual environment
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# kill any existing gunicorn process
pkill gunicorn 2>/dev/null || true

# start nginx
sudo systemctl restart nginx

# run the application (foreground, Ctrl+C to stop)
gunicorn -w 4 -b 0.0.0.0:8000 app:app
