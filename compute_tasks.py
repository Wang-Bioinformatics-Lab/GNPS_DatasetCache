from celery import Celery
import os
import uuid
import requests


# Setting up celery
celery_instance = Celery('compute_tasks', backend='redis://redis', broker='redis://redis')

def populate_ftp():
    all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=0&offset=0&query=").json()
    print("X")


celery_instance.conf.beat_schedule = {
    "populate_ftp": {
        "task": "compute_tasks.populate_ftp",
        "schedule": 30.0
    }
}
