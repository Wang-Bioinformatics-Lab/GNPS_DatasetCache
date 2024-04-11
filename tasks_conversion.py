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
def convert_mri():
    return "XXX"