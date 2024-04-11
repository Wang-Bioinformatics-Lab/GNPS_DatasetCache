#!/bin/bash

celery -A tasks_conversion worker -l info -B -c 1 -Q conversion
