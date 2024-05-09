#!/bin/bash

celery -A tasks_compute purge -f # Purging on startup
celery -A tasks_compute worker -l info -B -c 4 -Q compute
