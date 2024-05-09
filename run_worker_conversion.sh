#!/bin/bash

celery -A tasks_conversion worker --autoscale=8,1 -l info -B -c 1 -Q conversion --max-tasks-per-child 10
