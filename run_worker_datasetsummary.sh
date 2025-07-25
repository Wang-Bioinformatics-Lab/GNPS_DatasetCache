#!/bin/bash

celery -A tasks_datasetsummary worker -l info -B -c 1 -Q datasetsummary
