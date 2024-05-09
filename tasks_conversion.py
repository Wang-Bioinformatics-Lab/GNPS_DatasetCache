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


# limit to 10 min
@celery_instance.task(time_limit=600)
def convert_mri(mri):
    # hashing the mri to get a unique identifier using uuid
    conversion_hashed_path = utils_conversion.determine_mri_path(mri)
    conversion_staging_filefolder = os.path.join(utils_conversion.CONVERSION_STAGING_FOLDER, conversion_hashed_path)
    conversion_output_filefolder = os.path.join(utils_conversion.CONVERSION_RESULT_FOLDER, conversion_hashed_path)

    # Checking if this file already has been converted, if so, then we do nothing
    if utils_conversion.status_mri(mri) is True:
        return "Already Converted"
    
    path_to_full_raw_filename = utils_conversion.download_mri(mri, conversion_staging_filefolder, cache_url="http://gnps-datasetcache-datasette:5234")

    # We can now run msconvert on it
    utils_conversion.convert_mri(path_to_full_raw_filename, conversion_staging_filefolder)

    # now that we converted, lets move it to the converted folder
    converted_files = glob.glob(os.path.join(conversion_staging_filefolder, "*.mzML"))

    if len(converted_files) == 1:
        # making sure it exists
        os.makedirs(conversion_output_filefolder, exist_ok=True)
        output_filename = os.path.join(conversion_output_filefolder, os.path.basename(converted_files[0]))
        
        # moving over
        shutil.move(converted_files[0], output_filename)

    
    # is ia file or a folder
    # if os.path.isdir(path_to_full_raw_filename):
    #     shutil.rmtree(path_to_full_raw_filename)
    # else:
    #     os.remove(path_to_full_raw_filename)


celery_instance.conf.task_routes = {
    # conversion
    'tasks_conversion.convert_mri': {'queue': 'conversion'},
}