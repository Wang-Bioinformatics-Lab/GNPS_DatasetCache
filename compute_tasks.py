from celery import Celery
import os
import uuid
import requests
import utils
import sys

# Setting up celery
celery_instance = Celery('compute_tasks', backend='redis://redis', broker='redis://redis')

@celery_instance.task
def populate_ftp():
    all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=0&offset=0&query=").json()
    print("X", file=sys.stderr)


celery_instance.conf.beat_schedule = {
    "populate_ftp": {
        "task": "compute_tasks.populate_ftp",
        "schedule": 5.0
    }
}
