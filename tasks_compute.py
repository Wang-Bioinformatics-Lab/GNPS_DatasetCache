from celery import Celery
import os
import uuid
import requests
import utils
import sys
import subprocess
from pathlib import Path
from models import Filename
from models import UniqueMRI

import pandas as pd
import datetime
import werkzeug
import json
import dotenv
import time
from tqdm import tqdm

# Setting up celery
celery_instance = Celery('tasks_compute', backend='redis://gnps-datasetcache-redis', broker='redis://gnps-datasetcache-redis')

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


# Here we have a global refresh all that coordinates the logic
@celery_instance.task()
def refresh_all():
    # we will call the tasks here as subtasks
    mwb_mtbls_files_result = calculate_repository_files.delay()

    # Wait for task to be done
    while(True):
        # checking if done
        if mwb_mtbls_files_result.ready():
            break

        # sleep
        print("WAITING FOR MTBLS/MWB TO FINISH", file=sys.stderr, flush=True)
        time.sleep(60)

    # once these files are done, we want to populate
    populate_mwb_files.delay()
    populate_mtbls_files.delay()
    populate_msv_files.delay()

    # we should consider doing MassIVE at the end
    #populate_all_massive.delay()

    # finally we want to populate the output into the database
    populate_unique_file_usi.delay()

    return ""

# Here we are going ot calculate the files, runs at most for 48 hours
@celery_instance.task(time_limit=172800)
def calculate_repository_files():
    # running the nextflow command
    dotenv.load_dotenv()
    nextflow_cmd = "cd /app/workflows && nextflow run /app/workflows/create_file_lists_workflow.nf \
        --mtblstoken {} -c ./nextflow.config \
        > nextflow_stdout.log".format(os.environ["MTBLS_TOKEN"])

    import subprocess
    process = subprocess.Popen(nextflow_cmd, shell=True)

    # Wait for the process to complete
    process.wait()

    # Get the return code
    return_code = process.returncode

    # Print the return code
    print("Return code - NEXTFLOW DATASET LISTS:", return_code)



def _import_msv_files(files_df):
    for record in tqdm(files_df.to_dict(orient="records")):
        try:
            usi = record["usi"]
            filepath = record["filepath"]
            dataset_accession = record["dataset"]
            sample_type = record["sample_type"]
            collection_name = record["collection"]
            is_update = record["is_update"]
            update_name = record["update_name"]
            create_time = record["create_time"]
            size = record["size"]
            size_mb = record["size_mb"]

            filename_db = Filename.get_or_create(
                                            usi=usi,
                                            filepath=filepath, 
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

def _import_mwb_mtbls_files(files_df, repo="MWB"):
    
    for record in tqdm(files_df.to_dict(orient="records")):
        # cleaning up the paths
        dataset_accession = record["study_id"]
        filepath = record["file_path"]
        #filepath = filepath.replace("/nfs/public/rw/metabolomics/prod/data/studies/metadata-files/{}/".format(dataset_accession), "")


        usi = "mzspec:{}:{}".format(dataset_accession, filepath)
        filename = filepath
        sample_type = repo
        collection_name = ""
        is_update = 0
        update_name = ""
        create_time = datetime.datetime.now()
        size = 0
        size_mb = int( size / 1024 / 1024 )

        try:
            filename_db = Filename.get_or_create(
                                            usi=usi,
                                            filepath=filename, 
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

def _import_unique_mri_files(files_df):
    print("IMPORTING UNIQUE MRI", file=sys.stderr, flush=True)

    for record in tqdm(files_df.to_dict(orient="records")):
        try:
            usi = record["usi"]
            filepath = record["filepath"]
            dataset_accession = record["dataset"]
            sample_type = record["sample_type"]
            collection_name = record["collection"]
            is_update = record["is_update"]
            update_name = record["update_name"]
            create_time = record["create_time"]
            size = record["size"]
            size_mb = record["size_mb"]

            uniquemir_db = UniqueMRI.get_or_create(
                                            usi=usi,
                                            filepath=filepath, 
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

# @celery_instance.task(rate_limit='1/h')
# def populate_all_massive():
#     Filename.create_table(True)

#     #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=0&offset=0&query=").json()["row_data"]
#     #all_dataset_list = requests.get("https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=300&offset=9001&query=").json()["row_data"]
#     #all_dataset_list.reverse()

#     # Populating GNPS
#     offset = 0

#     while True:
#         url = "https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize=10&offset={}&query=%23%7B%22query%22%3A%7B%7D%2C%22table_sort_history%22%3A%22createdMillis_dsc%22%7D".format(offset)
#         r = requests.get(url)

#         try:
#             r.raise_for_status()
#         except:
#             break

#         dataset_list = r.json()["row_data"]

#         for dataset in dataset_list:
#             accession = dataset["dataset"]
#             print("Scheduling", accession)
#             populate_massive_dataset.delay(accession)

#         offset += 10

@celery_instance.task
def populate_msv_files():
    # Reading the file and inserting into the database
    df = pd.read_csv("workflows/nf_output/GNPSFilePaths_ALL.tsv", sep="\t")

    _import_msv_files(df)

    return 0


@celery_instance.task
def populate_mwb_files():
    # We assume that we have already run the workflow
    # addressing mwb
    df = pd.read_csv("workflows/nf_output/MWBFilePaths_ALL.tsv", sep="\t")

    _import_mwb_mtbls_files(df, repo="MWB")

    return 0

@celery_instance.task
def populate_mtbls_files():
    # We assume that we have already run the workflow
    # addressing mtbls
    df = pd.read_csv("workflows/nf_output/MetabolightsFilePaths_ALL.tsv", sep="\t")

    _import_mwb_mtbls_files(df, repo="MTBLS")

    return 0

@celery_instance.task
def populate_unique_file_usi():
    # Reading the file and inserting into the database
    
    df = pd.read_csv("workflows/nf_output/all_unique_mri.tsv", sep="\t")

    _import_unique_mri_files(df)

    return 0

# Going to massive and index all files
@celery_instance.task
def populate_massive_dataset(dataset_accession):
    print("processing", dataset_accession)
    all_dataset_files = utils._get_massive_files(dataset_accession, acceptable_extensions=[], method="https")

    print("Found", len(all_dataset_files), "files")

    dataset_information = requests.get("http://massive.ucsd.edu/ProteoSAFe/proxi/v0.1/datasets/{}".format(dataset_accession)).json()
    dataset_title = dataset_information["title"]
    sample_type = "MASSIVE"

    if "gnps" in dataset_title.lower():
        sample_type = "GNPS"
        
    for filedict in all_dataset_files:
        try:
            filename = filedict["path"]
            size = filedict["size"]
            size_mb = int( size / 1024 / 1024 )
            create_time = datetime.datetime.fromtimestamp(filedict["timestamp"])

            # Cleaning up the MassIVE in the file path
            filename = filename[13:]

            usi = "mzspec:{}:{}".format(dataset_accession, filename)

            collection_name, is_update, update_name =  _get_file_metadata(filename)
            filename_db = Filename.get_or_create(
                                                usi=usi,
                                                filepath=filename, 
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

# Reading the json files summarizing each file and inserting it into the database
@celery_instance.task(rate_limit='1/m')
def precompute_all_datasets():
    raise Exception("Need to Reimplement")

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

# Finding the files that do not have a json, then we will actually do the expensive thing to compute it. 
@celery_instance.task(rate_limit='1/h')
def recompute_all_datasets():
    raise Exception("Need to Reimplement")

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
        # if filename.sample_type == "DEFAULT":
        #     continue

        acceptable_extensions = [".mzML", ".mzXML", ".mzml", ".mzxml"]
        #acceptable_extensions = [".mzML"]

        # Lets not handle HUGE files
        if filename.size_mb > 2000:
            continue

        if file_extension in acceptable_extensions:
            recompute_file.delay(filepath)

# Dumping the database to a file
@celery_instance.task(rate_limit='1/h')
def dump():
    url = "http://gnps-datasetcache-datasette:5234/datasette/database/filename.csv?_stream=on&_size=max"
    output_file = "./database/dump.csv"
    wget_cmd = "wget '{}' -O {} 2> /dev/null".format(url, output_file)

    os.system(wget_cmd)


# Recomputing a single file
@celery_instance.task(time_limit=480)
def recompute_file(filepath):
    raise Exception("Need to Reimplement")

    filename_db = Filename.get(Filename.filepath == filepath)

    # Skipping if we already have seen it
    try:
        if filename_db.spectra_ms1 > 0 or filename_db.spectra_ms2 > 0:
            return
        
        if filename_db.file_processed != "No":
            return
    except:
        return

    # We are going to see if we can do anything with mzML files
    ftp_path = "ftp://massive.ucsd.edu/{}".format(filepath)

    output_json_filename = os.path.join("/app/database/json/", werkzeug.utils.secure_filename(ftp_path) + ".json")
    if os.path.exists(output_json_filename):
        return

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
        filename_db.file_processed = "DONE"

        filename_db.save()

        # Trying to save the json information for future use
        with open(output_json_filename, "w") as o:
            o.write(json.dumps(summary_dict))
    except:
        filename_db.file_processed = "FAILED"
        filename_db.save()

        pass
    
    os.remove(output_filename)


celery_instance.conf.beat_schedule = {
    "refresh_all": {
        "task": "tasks_compute.refresh_all",
        "schedule": 86400
    },
    "dump": {
        "task": "tasks_compute.dump",
        "schedule": 86400
    }
}

celery_instance.conf.task_routes = {
    # This is just for scheduling and only one can run at a time
    'tasks_compute.refresh_all': {'queue': 'beat'},
    'tasks_compute.dump': {'queue': 'beat'},
    
    # This is doing the actual work
    'tasks_compute.calculate_repository_files': {'queue': 'compute'},

    'tasks_compute.populate_mwb_files': {'queue': 'compute'},    
    'tasks_compute.populate_mtbls_files': {'queue': 'compute'},    
    'tasks_compute.populate_msv_files': {'queue': 'compute'},
    'tasks_compute.populate_unique_file_usi': {'queue': 'compute'},
}