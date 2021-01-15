#!/bin/bash

#celery -A tasks worker -l info -c 6 -Q compute --max-tasks-per-child 10 --loglevel INFO
celery -A compute_tasks worker -l info -B -c 1
