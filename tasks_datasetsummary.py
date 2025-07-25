from celery import Celery
import sys
import os
import json
import requests
import errno
import glob
import shutil
import uuid
import glob

celery_instance = Celery('compute_tasks', backend='redis://gnps-datasetcache-redis', broker='redis://gnps-datasetcache-redis')


# limit to 10 min
@celery_instance.task(time_limit=84600)
def calculate_dataset_summaries():
    print("Processing")

    # finding all the datasets
    massive_datasets_list = glob.glob("/data/datasets/server/All_Repos/MassIVE/*")
    st_datasets_list = glob.glob("/data/datasets/server/All_Repos/ST/*")
    mtbls_datasets_list = glob.glob("/data/datasets/server/All_Repos/MTBLS/*")
    norman_datasets_list = glob.glob("/data/datasets/server/All_Repos/Norman/*")

    all_datasets_list = massive_datasets_list + st_datasets_list + mtbls_datasets_list + norman_datasets_list

    # shuffle the order to randomize
    import random
    random.shuffle(all_datasets_list)

    for dataset_path in all_datasets_list:
        print("Processing dataset:", dataset_path, flush=True)
        dataset_name = os.path.basename(dataset_path)

        output_path = "/app/workflows/PerScanSummarizer_Workflow/nf_output/{}".format(dataset_name)

        # TODO CALL THE NEXTFLOW HERE
        import sys
        print("RUNNING DATASET SUMMARY WORKFLOW", file=sys.stderr, flush=True)

        path_to_script  = "/app/workflows/PerScanSummarizer_Workflow/nf_workflow.nf"
        work_dir = "/data/gscratch/web-services/PerScanSummarizer_Workflow/work"
        stdout_log = "/app/workflows/perscansummarizer_workflow.log"
        nextflow_config = "/app/workflows/PerScanSummarizer_Workflow/nextflow_docker_pipeline.config"

        # Use subprocess to run a nextflow script to generate all everything we need
        cmd = " ".join([
            "nextflow", "run", path_to_script, 
            "--inputspectra", dataset_path,
            "--output_dir", output_path,
            "-c", nextflow_config,
            "-w", work_dir,
            "-resume"
        ])

        cmd = "export MAMBA_ALWAYS_YES='true' && {} >> {}".format(cmd, stdout_log)
        print("Running command:", cmd, flush=True, file=sys.stderr)
        os.system(cmd)



celery_instance.conf.task_routes = {
    'tasks_datasetsummary.calculate_dataset_summaries': {'queue': 'datasetsummary'},
}