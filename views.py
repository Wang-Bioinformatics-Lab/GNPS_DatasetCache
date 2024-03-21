# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, send_file, make_response, Response

from app import app
from models import *

import os
import csv
import json
import uuid
import requests

import compute_tasks

def _count_number_of_datasets():
    return Filename.select().group_by(Filename.dataset).count()

@app.route('/', methods=['GET'])
def renderhomepage():
    db_count = Filename.select().count()
    raw_db_count = Filename.select().where(Filename.collection == "raw").count()
    ccms_peak_db_count = Filename.select().where(Filename.collection == "ccms_peak").count()
    peak_db_count = Filename.select().where(Filename.collection == "peak").count()

    # Counting number of datasets
    dataset_count = _count_number_of_datasets()

    return render_template('homepage.html', 
                            db_count=db_count, 
                            raw_db_count=raw_db_count, 
                            ccms_peak_db_count=ccms_peak_db_count, 
                            peak_db_count=peak_db_count,
                            dataset_count=dataset_count)

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


@app.route('/heartbeat', methods=['GET'])
def testapi():
    return_obj = {}
    return_obj["status"] = "success"
    return json.dumps(return_obj)

@app.route('/calculatefilelists', methods=['GET'])
def calcualtefilelist():
    compute_tasks.calculate_mwb_mtbls_files.delay()
    return "Calculating all File Lists"



@app.route('/refresh', methods=['GET'])
def refresh():
    compute_tasks.populate_all_datasets.delay()
    return "refreshing all datasets"

@app.route('/refresh/massivedataset', methods=['GET'])
def refresh_dataset():
    dataset = request.args.get('dataset')

    compute_tasks.populate_dataset.delay(dataset)
    
    return "refreshing dataset {}"


# @app.route('/recompute', methods=['GET'])
# def recompute():
#     compute_tasks.recompute_all_datasets.delay()
#     return "recompute"

# @app.route('/precompute', methods=['GET'])
# def precompute():
#     compute_tasks.precompute_all_datasets.delay()
#     return "precompute"

@app.route('/dump', methods=['GET'])
def dump():
    compute_tasks.dump.delay()
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

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/database/'):
        return redirect("/datasette" + request.full_path)
        
    # note that we set the 404 status explicitly
    return "NOT FOUND", 404