#!/bin/bash

celery -A compute_tasks worker -l info -B -c 2 -Q compute
