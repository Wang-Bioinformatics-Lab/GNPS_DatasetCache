from celery import Celery
import os
import json
import requests
import errno
import glob
import shutil
import uuid
import utils_conversion

celery_instance = Celery('compute_tasks', backend='redis://gnps-datasetcache-redis', broker='redis://gnps-datasetcache-redis')

@celery_instance.task()
def convert_mri(mri):
    path_to_full_raw_filename = utils_conversion.download_mri(mri, "temp/conversion_staging")

    # We can now run msconvert on it
    utils_conversion.convert_mri(path_to_full_raw_filename, "temp/conversion_staging")

    # TODO: clean up raw data


celery_instance.conf.task_routes = {
    # conversion
    'tasks_conversion.convert_mri': {'queue': 'conversion'},
}