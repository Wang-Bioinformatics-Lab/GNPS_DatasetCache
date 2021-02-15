
import pandas as pd
import requests
import os
import ftputil
import pymzml
import subprocess
import io
import glob
import ming_proteosafe_library
import yaml

def _call_external_tool(cmd, timeout=90):
    """This calls the external tool but also does proper cleanup by killing all child processes

    Args:
        cmd ([type]): [description]
        timeout (int, optional): [description]. Defaults to 90.
    """

    try:
        p = subprocess.Popen([cmd], shell=True)
        p.wait(timeout=timeout)
        return 0
    except subprocess.TimeoutExpired:
        # Killing off child and all other children
        import psutil
        parent_pid = p.pid
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

    return 1

def _get_massive_files(dataset_accession, acceptable_extensions=[".mzml", ".mzxml", ".cdf", ".raw"]):
    massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")

    all_files = ming_proteosafe_library.get_all_files_in_dataset_folder_ftp(dataset_accession, "", 
                                                                            includefilemetadata=True, 
                                                                            massive_host=massive_host)

    if len(acceptable_extensions) > 0:
        all_files = [filename for filename in all_files if os.path.splitext(filename["path"])[1].lower() in acceptable_extensions]

    return all_files

def get_all_run_information(local_filename, msaccess_path="./bin/msaccess"):
    # Calculate information
    summary_dict = _calculate_file_stats(local_filename)
    
    # Calculate metadata
    run_metadata = _calculate_file_metadata(local_filename)

    # Trying to save the json information for future use
    summary_dict["run_metadata"] = run_metadata

    return summary_dict


def _calculate_image(local_filename, output_image_filename, msaccess_path="./bin/msaccess"):
    try:
        cmd = [msaccess_path, local_filename, "-x",  'image width=1920 height=1080']

        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=my_env)
        out = proc.communicate()[0]

        local_png = glob.glob("*png")[0]
        os.rename(local_png, output_image_filename)
    except:
        pass
    

def _calculate_file_scanslist(local_filename, output_summary_scans, msaccess_path="./bin/msaccess"):
    summary_df = pd.DataFrame()

    try:
        cmd = [msaccess_path, local_filename, "-x",  'spectrum_table delimiter=tab']

        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=my_env)
        out = proc.communicate()[0]

        local_scans = glob.glob("*tsv")[0]
        os.rename(local_scans, output_summary_scans)
    except:
        pass

    return summary_df


def _calculate_file_metadata(local_filename, msaccess_path="./bin/msaccess", timeout=90):
    metadata_dict = {}

    try:
        cmd = [msaccess_path, local_filename, "-x",  'metadata']

        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=my_env)
        proc.wait(timeout=timeout)

        out = proc.communicate()[0]

        local_metadata = glob.glob("*metadata.txt")[0]
        yaml_string = open(local_metadata).read()
        yaml_string = yaml_string.replace("dataProcessingList", "dataProcessingList:")
        metadata_dict = yaml.safe_load(yaml_string)
        os.remove(local_metadata)
    except subprocess.TimeoutExpired:
        # Killing off child and all other children
        import psutil
        parent_pid = proc.pid
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        raise
    except:
        pass

    return metadata_dict


def _calculate_file_stats(local_filename, msaccess_path="./bin/msaccess", timeout=90):
    MS_precisions = {
        1 : 5e-6,
        2 : 20e-6,
        3 : 20e-6
    }

    response_dict = {}

    try:
        cmd = [msaccess_path, local_filename, "-x",  'run_summary delimiter=tab']

        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=my_env)
        proc.wait(timeout=timeout)
        out = proc.communicate()[0]

        all_lines = str(out).replace("\\t", "\t").split("\\n")
        all_lines = [line for line in all_lines if len(line) > 10 ]
        updated_version = "\n".join(all_lines)
                
        data = io.StringIO(updated_version)
        df = pd.read_csv(data, sep="\t")
        
        record = df.to_dict(orient='records')[0]

        fields = ["Vendor", "Model", "MS1s", "MS2s"]
        for field in fields:
            if field in record:
                response_dict[field] = record[field]
            else:
                response_dict[field] = "N/A"

    except subprocess.TimeoutExpired:
        # Killing off child and all other children
        import psutil
        parent_pid = proc.pid
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        raise
    except:
        pass
    
    return response_dict