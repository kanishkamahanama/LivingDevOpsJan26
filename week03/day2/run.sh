#!/bin/bash

# Database Configuration - Update these with your RDS details
export DB_HOST="jan26week3-db-instance.c4hw00gywz3b.us-east-1.rds.amazonaws.com"
export DB_NAME="jan26week3db"
export DB_USER="postgres"
export DB_PASSWORD="Admin1234"
export DB_PORT="5432"
export DB_SSL_MODE="require"

# create a virtual environment
python3 -m venv .venv

# activate the virtual environment
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# kill any existing gunicorn process
pkill gunicorn 2>/dev/null || true

# start nginx
# sudo systemctl restart nginx -  commented out as ALB will use in this demo)

# Run the database initialization script
python init_db.py

# run the application (foreground, Ctrl+C to stop)
gunicorn -w 4 -b 0.0.0.0:8000 app:app
