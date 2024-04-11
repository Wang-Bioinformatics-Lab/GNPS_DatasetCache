#!/bin/bash

celery -A tasks_conversion worker -l info -B -c 4 -Q conversion
