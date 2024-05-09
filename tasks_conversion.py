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
    # hashing the mri to get a unique identifier using uuid
    conversion_hashed_path = utils_conversion.determine_mri_path(mri)

    conversion_staging_filefolder = os.path.join(utils_conversion.CONVERSION_STAGING_FOLDER, conversion_hashed_path)

    path_to_full_raw_filename = utils_conversion.download_mri(mri, conversion_staging_filefolder, cache_url="http://gnps-datasetcache-datasette:5234")

    # We can now run msconvert on it
    conversion_output_filefolder = os.path.join(utils_conversion.CONVERSION_RESULT_FOLDER, conversion_hashed_path)
    utils_conversion.convert_mri(path_to_full_raw_filename, conversion_output_filefolder)

    # TODO: clean up staging


celery_instance.conf.task_routes = {
    # conversion
    'tasks_conversion.convert_mri': {'queue': 'conversion'},
}