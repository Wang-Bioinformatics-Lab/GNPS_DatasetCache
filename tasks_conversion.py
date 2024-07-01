from celery import Celery
import os
import json
import requests
import errno
import glob
import shutil
import uuid
import utils_conversion
from celery_once import QueueOnce


celery_instance = Celery('compute_tasks', backend='redis://gnps-datasetcache-redis', broker='redis://gnps-datasetcache-redis')

# Limiting the once queue for celery tasks, will give an error for idempotent tasks within an hour interval
celery_instance.conf.ONCE = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': 'redis://gnps-datasetcache-redis:6379/0',
    'default_timeout': 60 * 10,
    'blocking': False,
  }
}

# limit to 10 min
@celery_instance.task(time_limit=600, base=QueueOnce)
def convert_mri(mri):
    print("Processing", mri)

    # hashing the mri to get a unique identifier using uuid
    conversion_hashed_path = utils_conversion.determine_mri_path(mri)
    conversion_staging_filefolder = os.path.join(utils_conversion.CONVERSION_STAGING_FOLDER, conversion_hashed_path)
    conversion_output_filefolder = os.path.join(utils_conversion.CONVERSION_RESULT_FOLDER, conversion_hashed_path)

    # Checking if this file already has been converted, if so, then we do nothing
    if utils_conversion.status_mri(mri) is True:
        print("Already Converted", mri)
        return "Already Converted"
    
    print("Downloading", mri)
    path_to_full_raw_filename = utils_conversion.download_mri(mri, conversion_staging_filefolder, cache_url="http://gnps-datasetcache-datasette:5234")D

    # We can now run msconvert on it
    print("Converting", mri, "with MSConvert")
    utils_conversion.convert_mri(path_to_full_raw_filename, conversion_staging_filefolder)

    # now that we converted, lets move it to the converted folder
    converted_files = glob.glob(os.path.join(conversion_staging_filefolder, "*.mzML"))

    if len(converted_files) == 1:
        # making sure it exists
        os.makedirs(conversion_output_filefolder, exist_ok=True)
        output_filename = os.path.join(conversion_output_filefolder, os.path.basename(converted_files[0]))
        
        # moving over
        shutil.move(converted_files[0], output_filename)

    
    # is it a file or a folder
    print("Cleaning up", mri)
    if os.path.isdir(path_to_full_raw_filename):
        shutil.rmtree(path_to_full_raw_filename)
    else:
        os.remove(path_to_full_raw_filename)


celery_instance.conf.task_routes = {
    # conversion
    'tasks_conversion.convert_mri': {'queue': 'conversion'},
}