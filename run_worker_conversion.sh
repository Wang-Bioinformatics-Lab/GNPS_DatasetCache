#!/bin/bash

celery -A tasks_conversion worker --autoscale=8,1 -l debug -B -Q conversion --max-tasks-per-child 10
