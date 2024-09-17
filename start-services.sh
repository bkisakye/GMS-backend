#!/bin/bash
# Activate virtual environment
source /home/bkisakye/Desktop/GMS/BaylorGrants/venv/bin/activate

# Start Redis server
redis-server --daemonize yes

# Start Celery Worker
/home/bkisakye/Desktop/GMS/BaylorGrants/venv/bin/celery -A BaylorGrants worker --loglevel=info --detach

# Start Celery Beat
/home/bkisakye/Desktop/GMS/BaylorGrants/venv/bin/celery -A BaylorGrants beat --loglevel=info --detach
