#!/bin/bash

#celery -A tasks worker -l info -c 6 -Q compute --max-tasks-per-child 10 --loglevel INFO
celery -A tasks_compute purge -f # Purging on startup
celery -A tasks_compute worker -l info -B -c 1 -Q beat
