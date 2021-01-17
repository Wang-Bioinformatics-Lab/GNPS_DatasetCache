#!/bin/bash

celery -A compute_tasks worker -l info -B -c 3 -Q compute
