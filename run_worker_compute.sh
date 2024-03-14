#!/bin/bash

celery -A compute_tasks purge -f # Purging on startup
celery -A compute_tasks worker -l info -B -c 4 -Q compute
