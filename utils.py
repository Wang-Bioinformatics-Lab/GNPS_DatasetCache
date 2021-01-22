
import pandas as pd
import requests
import os
import ftputil
import pymzml
import subprocess
import io
import ming_proteosafe_library


def _get_massive_files(dataset_accession, acceptable_extensions=[".mzml", ".mzxml", ".cdf", ".raw"]):
    massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")

    all_files = ming_proteosafe_library.get_all_files_in_dataset_folder_ftp(dataset_accession, "", 
                                                                            includefilemetadata=True, 
                                                                            massive_host=massive_host)

    if len(acceptable_extensions) > 0:
        all_files = [filename for filename in all_files if os.path.splitext(filename["path"])[1].lower() in acceptable_extensions]

    return all_files

def _calculate_file_stats(local_filename):
    MS_precisions = {
        1 : 5e-6,
        2 : 20e-6,
        3 : 20e-6
    }

    response_dict = {}

    try:
        cmd = ["./bin/msaccess", local_filename, "-x",  'run_summary delimiter=tab']

        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=my_env)
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
    except:
        pass
    
    return response_dict