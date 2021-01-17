#!/bin/bash
#export FLASK_ENV=development
#python ./main.py

python ./create_database.py
gunicorn -w 4 --threads=6 --worker-class=gthread -b 0.0.0.0:5000 --timeout 120 --max-requests 500 --max-requests-jitter 100 --graceful-timeout 120 main:app --access-logfile /app/logs/access.log
