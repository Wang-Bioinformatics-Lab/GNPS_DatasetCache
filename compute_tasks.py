from celery import Celery
import os
import uuid
import requests
import utils
import sys
from pathlib import Path
from models import Filename

import datetime

# Setting up celery
celery_instance = Celery('compute_tasks', backend='redis://redis', broker='redis://redis')

def _get_file_metadata(msv_path):
    """
    This assume a path like this MSV000082975/peak/Kermit_20130425_PB_Nadine_U2_01.mzML. 

    We will calculate if its an update, update name and its collection

    Args:
        msv_path ([type]): [description]

    Returns:
        [type]: [description]
    """

    is_update = 0
    update_name = ""
    collection_name = ""

    my_path = Path(msv_path)
    all_parents = my_path.parents
    len_parents = len(all_parents)
    collection_path = all_parents[len_parents - 3]

    # If its an update, then we'll have to look a bit deeper
    collection_name = collection_path.name
    if collection_name == "updates":
        is_update = 1

        update_name = all_parents[len_parents - 4].name
        collection_name = all_parents[len_parents - 5].name

    return collection_name, is_update, update_name


@celery_instance.task
def populate_ftp():
    Filename.create_table(True)

    #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=0&offset=0&query=").json()["row_data"]
    #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=300&offset=9001&query=").json()["row_data"]
    all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/datasets_json.jsp").json()["datasets"]
    
    all_dataset_list.reverse()

    for dataset in all_dataset_list:
        accession = dataset["dataset"]
        print(accession)
        all_dataset_files = utils._get_massive_files(accession, acceptable_extensions=[])
        
        for filedict in all_dataset_files:
            try:
                filename = filedict["path"]
                size = filedict["size"]
                create_time = datetime.datetime.fromtimestamp(filedict["timestamp"])

                collection_name, is_update, update_name =  _get_file_metadata(filename)
                filename_db = Filename.get_or_create(filepath=filename, 
                                                    dataset=accession, 
                                                    collection=collection_name,
                                                    is_update=is_update,
                                                    update_name=update_name,
                                                    create_time=create_time,
                                                    size=size)
            except:
                pass

celery_instance.conf.beat_schedule = {
    "populate_ftp": {
        "task": "compute_tasks.populate_ftp",
        "schedule": 86400
    }
}

celery_instance.conf.task_routes = {
    'compute_tasks.populate_ftp': {'queue': 'beat'},
}