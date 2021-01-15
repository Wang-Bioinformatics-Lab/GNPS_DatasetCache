# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, send_file, make_response

from app import app
from models import *

import os
import csv
import json
import uuid
import requests

import compute_tasks

@app.route('/', methods=['GET'])
def renderhomepage():
    db_count = Filename.select().count()
    raw_db_count = Filename.select().where(Filename.collection == "raw").count()
    ccms_peak_db_count = Filename.select().where(Filename.collection == "ccms_peak").count()
    peak_db_count = Filename.select().where(Filename.collection == "peak").count()
    return render_template('homepage.html', db_count=db_count, raw_db_count=raw_db_count, ccms_peak_db_count=ccms_peak_db_count, peak_db_count=peak_db_count)

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


@app.route('/refresh', methods=['GET'])
def refresh():
    compute_tasks.populate_ftp.delay()
    return "REFRESHING"


