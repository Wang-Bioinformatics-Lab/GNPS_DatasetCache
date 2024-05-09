#!/bin/bash

celery -A tasks_conversion worker -l info -B –autoscale=8,1 -Q conversion
