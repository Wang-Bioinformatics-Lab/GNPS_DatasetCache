from celery import Celery
import os
import uuid
import requests
import utils
import sys
from pathlib import Path
from models import Filename

# Setting up celery
celery_instance = Celery('compute_tasks', backend='redis://redis', broker='redis://redis')

def _get_collection(msv_path):
    """
    This assume a path like this MSV000082975/peak/Kermit_20130425_PB_Nadine_U2_01.mzML

    Args:
        msv_path ([type]): [description]

    Returns:
        [type]: [description]
    """

    my_path = Path(msv_path)
    all_parents = my_path.parents
    len_parents = len(all_parents)
    collection_path = all_parents[len_parents - 3]
    
    return collection_path.name

@celery_instance.task
def populate_ftp():
    all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=0&offset=0&query=").json()["row_data"].reverse()
    #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=30&offset=9001&query=").json()["row_data"].reverse()
    for dataset in all_dataset_list:
        accession = dataset["dataset"]
        print(accession)
        all_dataset_files = utils._get_massive_files(accession)
        
        for filename in all_dataset_files:
            try:
                collection_name =  _get_collection(filename)
                filename_db = Filename.get_or_create(filepath=filename, dataset=accession, collection=collection_name)
            except:
                pass
            


celery_instance.conf.beat_schedule = {
    "populate_ftp": {
        "task": "compute_tasks.populate_ftp",
        "schedule": 86400
    }
}
