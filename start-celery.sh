#!/bin/bash

# Set Django settings module
export DJANGO_SETTINGS_MODULE=BaylorGrants.settings

# Activate the virtual environment
source venv/bin/activate

# Start Celery worker
echo "Starting Celery worker..."
celery -A BaylorGrants worker --loglevel=info --detach
if [ $? -eq 0 ]; then
    echo "Celery worker started successfully."
else
    echo "Failed to start Celery worker!" >&2
    exit 1
fi

# Start Celery beat
echo "Starting Celery beat..."
celery -A BaylorGrants beat --loglevel=info --detach
if [ $? -eq 0 ]; then
    echo "Celery beat started successfully."
else
    echo "Failed to start Celery beat!" >&2
    exit 1
fi
