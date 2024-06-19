#!/bin/bash

#celery -A tasks_compute worker -l info -B -c 1 -Q workflowsserialqueue --detach
celery -A tasks_compute worker -l info -B -c 1 -Q compute
