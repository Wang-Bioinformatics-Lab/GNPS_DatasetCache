# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, send_file, make_response, Response

from app import app
from models import *

import os
import csv
import json
import uuid
import requests
import glob
import datetime
import pandas as pd

import tasks_compute
import tasks_conversion

import utils_conversion

import config

def _count_number_of_datasets():
    return Filename.select().group_by(Filename.dataset).count()

@app.route('/', methods=['GET'])
def renderhomepage():
    # try getting file count
    try:
        db_count = Filename.select().count()
    except:
        pass

    return render_template('homepage.html')

@app.route('/status.json', methods=['GET'])
def status():
    # Getting the status of everything
    status_dict = {}

    # Getting date of mwb file
    try:
        # getting last edit date of this file config.PATH_TO_MWB_FILES
        mwb_file_date = os.path.getmtime(config.PATH_TO_MWB_FILES)
        
        # convert to datetime
        dt_object = datetime.datetime.fromtimestamp(mwb_file_date)
        
        # convert to PST
        dt_object = dt_object - datetime.timedelta(hours=7)

        datetime_string = dt_object.strftime('%Y-%m-%d %H:%M:%S')

        status_dict["MWB_TIMESTAMP"] = datetime_string
    except:
        status_dict["MWB_TIMESTAMP"] = "Can't calculate"


    # getting mtbls file
    try:
        # getting last edit date of this file config.PATH_TO_MTBLS_FILES
        mtbls_file_date = os.path.getmtime(config.PATH_TO_MTBLS_FILES)

        dt_object = datetime.datetime.fromtimestamp(mtbls_file_date)

        # convert to PST
        dt_object = dt_object - datetime.timedelta(hours=7)
        
        datetime_string = dt_object.strftime('%Y-%m-%d %H:%M:%S')

        status_dict["MTBLS_TIMESTAMP"] = datetime_string
    except:
        status_dict["MTBLS_TIMESTAMP"] = "Can't calculate"

    # Getting the file lists stdout
    try:
        with open("./workflows/nextflow_stdout.log", 'r') as file:
            nextflow_stdout_data = file.read()
        
        nextflow_stdout_modified = os.path.getmtime("./workflows/nextflow_stdout.log")
        nextflow_stdout_modified = str(pd.to_datetime(nextflow_stdout_modified, unit='s').tz_localize('UTC').tz_convert('US/Pacific'))
    except:
        nextflow_stdout_data = "No log file found"
        nextflow_stdout_modified = "N/A"

    # Getting the nextflow log
    try:
        with open("./workflows/.nextflow.log", 'r') as file:
            nextflow_log_data = file.read()
        
        nextflow_log_modified = os.path.getmtime("./workflows/.nextflow.log")
        nextflow_log_modified = str(pd.to_datetime(nextflow_log_modified, unit='s').tz_localize('UTC').tz_convert('US/Pacific'))
    except:
        nextflow_log_data = "No log file found"
        nextflow_log_modified = "N/A"

    # Doing cleanup on the nextflow log
    try:
        nextflow_log_data = nextflow_log_data.replace(os.environ["MTBLS_TOKEN"], "****")
    except:
        pass

    # Writing the nextflow information dict
    status_dict["nextflow"] = {
        "nextflow_stdout_modified" : nextflow_stdout_modified,
        "nextflow_stdout_data" : nextflow_stdout_data,
        "nextflow_log_modified" : nextflow_log_modified,
        "nextflow_log_data" : nextflow_log_data
    }
    
    return json.dumps(status_dict)

@app.route('/status.trace', methods=['GET'])
def status_trace():
    return send_file("./workflows/trace.txt")

@app.route('/status.timeline', methods=['GET'])
def status_timeline():
    return send_file("./workflows/timeline.html")


@app.route('/stats', methods=['GET'])
def renderstats():
    db_count = Filename.select().count()
    raw_db_count = Filename.select().where(Filename.collection == "raw").count()
    ccms_peak_db_count = Filename.select().where(Filename.collection == "ccms_peak").count()
    peak_db_count = Filename.select().where(Filename.collection == "peak").count()

    # Counting number of datasets
    dataset_count = _count_number_of_datasets()

    return render_template('stats.html', 
                            db_count=db_count, 
                            raw_db_count=raw_db_count, 
                            ccms_peak_db_count=ccms_peak_db_count, 
                            peak_db_count=peak_db_count,
                            dataset_count=dataset_count)

@app.route('/stats.json', methods=['GET'])
def renderstatsjson():
    db_count = Filename.select().count()
    massive_files_count = Filename.select().where(Filename.sample_type == "MASSIVE").count()
    gnps_files_count = Filename.select().where(Filename.sample_type == "GNPS").count()
    mwb_files_count = Filename.select().where(Filename.sample_type == "MWB").count()
    mtbls_files_count = Filename.select().where(Filename.sample_type == "MTBLS").count()

    # Counting number of datasets
    dataset_count = _count_number_of_datasets()

    output_dict = {}
    output_dict["files_count"] = db_count
    output_dict["dataset_count"] = dataset_count
    output_dict["massive_files_count"] = massive_files_count
    output_dict["gnps_files_count"] = gnps_files_count
    output_dict["mwb_files_count"] = mwb_files_count
    output_dict["mtbls_files_count"] = mtbls_files_count
    
    return json.dumps(output_dict)

@app.route('/dataset/<accession>/files', methods=['GET'])
def getfiles(accession):
    query_db = Filename.select().where(Filename.dataset == accession)

    all_results = []
    for db_row in query_db:
        result_dict = {}
        result_dict["filepath"] = db_row.filepath

        all_results.append(result_dict)

    return_obj = {}
    return_obj["count"] = query_db.count()
    return_obj["results"] = all_results
    
    return json.dumps(return_obj)

# End point to get the dump file for all the files
@app.route('/dataset/files', methods=['GET'])
def getallfiles():
    return send_file("./workflows/nf_output/all_dataset_files.csv", as_attachment=True)

# Getting some dump files from the workflow
@app.route('/dataset/uniquemri', methods=['GET'])
def getuniquemri():
    return send_file("./workflows/nf_output/database_unique_mri.csv", as_attachment=True)

@app.route('/dataset/nonredundantmri', methods=['GET'])
def nonredundantmri():
    return send_file("./workflows/nf_output/all_nonredundant_mri.tsv", as_attachment=True)

@app.route('/dataset/redundantmri', methods=['GET'])
def redundantmri():
    return send_file("./workflows/nf_output/all_redundantremoved_mri.tsv", as_attachment=True)

@app.route('/dataset/downloadmri', methods=['GET'])
def downloadmri():
    return send_file("./workflows/nf_output/download_mri.tsv", as_attachment=True)


@app.route('/heartbeat', methods=['GET'])
def testapi():
    status_obj = {}
    status_obj["status"] = "up"

    # checking the local disk free space
    disk = os.statvfs(".")
    free_space = disk.f_bavail * disk.f_frsize
    percent_free = disk.f_bavail / disk.f_blocks

    status_obj["percent_free"] = percent_free

    if percent_free < 0.1:
        status_obj["status"] = "error"
        status_obj["message"] = "Disk is almost full"

        return json.dumps(status_obj), 500

    return json.dumps(status_obj)



# Admin force updates
@app.route('/refresh/all', methods=['GET'])
def refresh_all():
    tasks_compute.refresh_all.delay()
    return "refresh_full_pipeline"

@app.route('/refresh/repository/files', methods=['GET'])
def refresh_repository_files():
    tasks_compute.calculate_repository_files.delay()
    return "refresh_repository_files"

@app.route('/refresh/mwb/import', methods=['GET'])
def refresh_mwb_import():
    tasks_compute.populate_mwb_files.delay()
    return "populate_mwb_files"

@app.route('/refresh/mtbls/import', methods=['GET'])
def refresh_mtbls_import():
    tasks_compute.populate_mtbls_files.delay()
    return "populate_mtbls_files"

@app.route('/refresh/massive/import', methods=['GET'])
def refresh_msv():
    tasks_compute.populate_msv_files.delay()
    return "populate_msv_files"

@app.route('/refresh/norman/import', methods=['GET'])
def refresh_norman():
    tasks_compute.populate_norman_files.delay()
    return "populate_norman_files"

@app.route('/refresh/mriset/import', methods=['GET'])
def populate_unique_file_usi():
    tasks_compute.populate_unique_file_usi.delay()
    return "populate_unique_file_usi"


@app.route('/dump', methods=['GET'])
def dump():
    tasks_compute.dump.delay()
    return "dump"

@app.route('/datasette/<path:path>',methods=['GET'])
def proxy(path):
    SITE_NAME = "http://gnps-datasetcache-datasette:5234/"
    if request.method=='GET':
        resp = requests.get(f'{SITE_NAME}{path}', params=request.values)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in     resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
    return response

###############################
# This is for dataset summary
###############################
import tasks_datasetsummary
@app.route('/refresh/datasetsummary', methods=['GET'])
def datasetsummary():
    tasks_datasetsummary.calculate_dataset_summaries.delay()
    return "calculate_dataset_summaries"

@app.route('/refresh/datasetsummary/import', methods=['GET'])
def classify_mri():
    tasks_compute.populate_uniquemri_computedinformation.delay()
    return "import_datasetsummary_mri"



###############################
# This is for conversion
###############################
@app.route('/convert/request', methods=['GET'])
def start_convert():
    # Get param mri
    mri = request.args.get('mri')

    try:
        tasks_conversion.convert_mri.delay(mri)
    except:
        pass
    
    return "converting {}".format(mri)

# This is for conversion
@app.route('/convert/status', methods=['GET'])
def status_convert():
    # Get param mri
    mri = request.args.get('mri')

    # We need to check if the file is there
    file_status = utils_conversion.status_mri(mri)

    status_dict = {}
    status_dict["status"] = file_status

    return json.dumps(status_dict)

@app.route('/convert/download', methods=['GET'])
def download_convert():
    # Get param mri
    mri = request.args.get('mri')

    # We need to check if the file is there
    file_status = utils_conversion.status_mri(mri)

    if file_status is True:
        conversion_hashed_path = utils_conversion.determine_mri_path(mri)

        conversion_folder = os.path.join(utils_conversion.CONVERSION_RESULT_FOLDER, conversion_hashed_path)

        # lets see if there is an mzML file in that folder
        mzml_files = glob.glob(os.path.join(conversion_folder, "*.mzML"))

        if len(mzml_files) > 0:
            return send_file(mzml_files[0], as_attachment=True)
        else:
            return "File not ready yet", 404
    else:
        return "File not ready yet", 404

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/database/'):
        return redirect("/datasette" + request.full_path)
        
    # note that we set the 404 status explicitly
    return "NOT FOUND", 404