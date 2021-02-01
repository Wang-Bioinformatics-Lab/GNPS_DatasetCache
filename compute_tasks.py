from celery import Celery
import os
import uuid
import requests
import utils
import sys
from pathlib import Path
from models import Filename

import datetime
import werkzeug
import json


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


@celery_instance.task(rate_limit='1/h')
def populate_all_datasets():
    Filename.create_table(True)

    #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=0&offset=0&query=").json()["row_data"]
    #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=300&offset=9001&query=").json()["row_data"]
    #all_dataset_list.reverse()

    all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/datasets_json.jsp").json()["datasets"]
    #all_dataset_list = all_dataset_list[:10] # DEBUG

    for dataset in all_dataset_list:
        accession = dataset["dataset"]
        print("Scheduling", accession)
        populate_dataset.delay(accession)
        

@celery_instance.task
def populate_dataset(dataset_accession):
    print("processing", dataset_accession)
    all_dataset_files = utils._get_massive_files(dataset_accession, acceptable_extensions=[])

    dataset_information = requests.get("http://massive.ucsd.edu/ProteoSAFe/proxi/v0.1/datasets/{}".format(dataset_accession)).json()
    dataset_title = dataset_information["title"]
    sample_type = "DEFAULT"

    if "gnps" in dataset_title.lower():
        sample_type = "GNPS"
        
    for filedict in all_dataset_files:
        try:
            filename = filedict["path"]
            size = filedict["size"]
            size_mb = int( size / 1024 / 1024 )
            create_time = datetime.datetime.fromtimestamp(filedict["timestamp"])

            collection_name, is_update, update_name =  _get_file_metadata(filename)
            filename_db = Filename.get_or_create(filepath=filename, 
                                                dataset=dataset_accession,
                                                sample_type=sample_type,
                                                collection=collection_name,
                                                is_update=is_update,
                                                update_name=update_name,
                                                create_time=create_time,
                                                size=size, 
                                                size_mb=size_mb)
        except:
            pass

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

@celery_instance.task(rate_limit='1/m')
def precompute_all_datasets():
    import glob
    import json
    all_json_files = glob.glob("database/precompute/**/*.json", recursive=True)

    for json_file in all_json_files:
        try:
            result_json = json.loads(open(json_file).read())
            filename = result_json["filename"].replace("/data/massive/public/", "").replace("/data/massive/", "")

            filename_db = Filename.get(Filename.filepath == filename)
            if filename_db.spectra_ms1 > 0 or filename_db.spectra_ms2 > 0:
                continue

            filename_db.spectra_ms1 = result_json["MS1s"]
            filename_db.spectra_ms2 = result_json["MS2s"]
            filename_db.instrument_vendor = result_json["Vendor"]
            filename_db.instrument_model = result_json["Model"]

            print("SAVED {}".format(filename))
        except:
            pass

@celery_instance.task(rate_limit='1/h')
def recompute_all_datasets():
    for filename in Filename.select():
        filepath = filename.filepath
        _, file_extension = os.path.splitext(filepath)

        # Skipping if we already have seen it
        try:
            if filename.spectra_ms1 > 0 or filename.spectra_ms2 > 0:
                continue
        except:
            continue

        # Skipping for now if not GNPS
        if filename.sample_type == "DEFAULT":
            continue

        acceptable_extensions = [".mzML", ".mzXML"]

        # We should relax this later
        # if filename.size_mb > 500 or filename.size_mb < 1:
        #     continue

        if file_extension in acceptable_extensions:
            recompute_file.delay(filepath)

@celery_instance.task(rate_limit='1/h')
def dump():
    url = "http://datasette:8001/datasette/database/filename.csv?_stream=on&_size=max"
    output_file = "./database/dump.csv"
    wget_cmd = "wget '{}' -O {} 2> /dev/null".format(url, output_file)

    os.system(wget_cmd)
            
@celery_instance.task
def recompute_file(filepath):
    filename_db = Filename.get(Filename.filepath == filepath)

    # Skipping if we already have seen it
    try:
        if filename_db.spectra_ms1 > 0 or filename_db.spectra_ms2 > 0:
            return
    except:
        return

    output_json_filename = os.path.join("/app/database/json/", werkzeug.utils.secure_filename(ftp_path) + ".json")
    if os.path.exists(output_json_filename):
        return
    
    # We are going to see if we can do anything with mzML files
    ftp_path = "ftp://massive.ucsd.edu/{}".format(filepath)

    output_filename = os.path.join("temp", werkzeug.utils.secure_filename(ftp_path))
    wget_cmd = "wget '{}' -O {} 2> /dev/null".format(ftp_path, output_filename)
    os.system(wget_cmd)


    try:
        summary_dict = utils.get_all_run_information(output_filename)
        summary_dict["filename"] = filepath

        filename_db.spectra_ms1 = safe_cast(summary_dict["MS1s"], int, 0)
        filename_db.spectra_ms2 = safe_cast(summary_dict["MS2s"], int, 0)
        filename_db.instrument_model = summary_dict["Model"]
        filename_db.instrument_vendor = summary_dict["Vendor"]

        filename_db.save()

        # Trying to save the json information for future use
        with open(output_json_filename, "w") as o:
            o.write(json.dumps(summary_dict))
    except:
        pass
    
    os.remove(output_filename)


celery_instance.conf.beat_schedule = {
    "populate_all_datasets": {
        "task": "compute_tasks.populate_all_datasets",
        "schedule": 864000
    },
    "recompute_all_datasets": {
        "task": "compute_tasks.recompute_all_datasets",
        "schedule": 1204000
    },
    "dump": {
        "task": "compute_tasks.dump",
        "schedule": 864000
    }
}

celery_instance.conf.task_routes = {
    'compute_tasks.populate_all_datasets': {'queue': 'beat'},
    'compute_tasks.recompute_all_datasets': {'queue': 'beat'},
    'compute_tasks.dump': {'queue': 'beat'},
    'compute_tasks.precompute_all_datasets': {'queue': 'beat'},
    'compute_tasks.populate_dataset': {'queue': 'compute'},
    'compute_tasks.recompute_file': {'queue': 'compute'}
}