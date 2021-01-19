#!/bin/bash

celery -A compute_tasks worker -l info -B -c 4 -Q compute
