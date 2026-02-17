#!/bin/bash

# Database Configuration - Set via environment variables
# These should be set in user-data.sh or exported before running this script
# Do NOT hardcode credentials here - this file is committed to GitHub

# Verify required environment variables are set
if [ -z "$DB_HOST" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "ERROR: Required database environment variables are not set!"
    echo "Please set: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD"
    echo ""
    echo "Example:"
    echo "  export DB_HOST='your-rds-endpoint.amazonaws.com'"
    echo "  export DB_NAME='your-database-name'"
    echo "  export DB_USER='postgres'"
    echo "  export DB_PASSWORD='your-password'"
    echo "  export DB_PORT='5432'"
    echo "  export DB_SSL_MODE='require'"
    exit 1
fi

# Set defaults for optional variables
export DB_PORT=${DB_PORT:-5432}
export DB_SSL_MODE=${DB_SSL_MODE:-require}

echo "Connecting to database at: $DB_HOST:$DB_PORT/$DB_NAME"


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
