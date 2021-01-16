
import pandas as pd
import requests
import os
import ftputil
import ming_proteosafe_library

def _get_massive_files(dataset_accession, acceptable_extensions=[".mzml", ".mzxml", ".cdf", ".raw"]):
    massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")

    all_files = ming_proteosafe_library.get_all_files_in_dataset_folder_ftp(dataset_accession, "", 
                                                                            includefilemetadata=True, 
                                                                            massive_host=massive_host)

    if len(acceptable_extensions) > 0:
        all_files = [filename for filename in all_files if os.path.splitext(filename["path"])[1].lower() in acceptable_extensions]

    return all_files
