import pandas as pd
import os
import argparse
import requests
import datetime
from tqdm import tqdm
from pathlib import Path

from gnpsdata import publicdata

def _get_massive_files(dataset_accession, acceptable_extensions=[".mzml", ".mzxml", ".cdf", ".raw", ".d"]):
    # we are using HTTP
    print("HTTP")
    try:
        all_files = publicdata.get_massive_public_dataset_filelist(dataset_accession)
    except:
        return []

    # Cleaning it up
    for file_obj in all_files:
        file_obj["path"] = file_obj["file_descriptor"][2:]

        # Updating time to timestamp
        file_obj["timestamp"] = file_obj["last_used_millis"] / 1000
        
    if len(acceptable_extensions) > 0:
        all_files = [filename for filename in all_files if os.path.splitext(filename["path"])[1].lower() in acceptable_extensions]

    return all_files

def _get_all_datasets():
    all_datasets = []
    offset = 0
    page_size = 1000

    while True:
        url = "https://massive.ucsd.edu/ProteoSAFe/QueryDatasets?pageSize={}&offset={}&query=%23%7B%22query%22%3A%7B%7D%2C%22table_sort_history%22%3A%22createdMillis_dsc%22%7D".format(page_size, offset)
        r = requests.get(url)

        try:
            r.raise_for_status()
        except:
            break

        dataset_list = r.json()["row_data"]

        if len(dataset_list) == 0:
            break

        for dataset in dataset_list:
            all_datasets.append(dataset)
        
        print("Got", len(dataset_list), "datasets", len(all_datasets), "total datasets", "currently at", offset)

        offset += page_size

    return all_datasets

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

    # If its an update, then we'll have to look a bit deeper
    collection_name = my_path.parts[0]
    if collection_name == "updates":
        is_update = 1

        update_name = all_parents[len_parents - 4].name
        collection_name = all_parents[len_parents - 5].name

    return collection_name, is_update, update_name


def main(args):
    print(args)

    # Getting the existing datasets
    if args.existing_datasets is not None:
        existing_datasets_df = pd.read_csv(args.existing_datasets)
        existing_datasets = set(existing_datasets_df["datasets"].values)
    else:
        existing_datasets = set()

    print("Found", len(existing_datasets), "existing datasets")

    # Getting all GNPS Datasets
    all_datasets = _get_all_datasets()

    # Filtering these datasets to only the ones that are not in the existing datasets
    filtered_all_datasets = []

    for dataset in all_datasets:
        dataset_accession = dataset["dataset"]
        
        # Skipping already imported
        if dataset_accession in existing_datasets:
            continue

        # TODO: Filtering if too small dataset accession
        try:
            accession_int = int(dataset_accession.replace("MSV", ""))
            if accession_int <= 78429:
                continue
        except:
            pass

        filtered_all_datasets.append(dataset)


    print("GETTING", len(filtered_all_datasets), "DATASETS")
    
    # DEBUG
    # filtered_all_datasets = filtered_all_datasets[:10]

    all_files_information = []

    # Getting each ones' files
    for dataset_information in tqdm(filtered_all_datasets):
        dataset_accession = dataset_information["dataset"]

        print("Addressing Files From ", dataset_accession)

        current_dataset_files = _get_massive_files(dataset_information["dataset"], acceptable_extensions=[])

        dataset_title = dataset_information["title"]
        sample_type = "MASSIVE"

        if "gnps" in dataset_title.lower():
            sample_type = "GNPS"
            
        for filedict in current_dataset_files:
            try:
                dataset_accession = dataset_information["dataset"]

                filename = filedict["path"]
                size = filedict["size"]
                size_mb = int( size / 1024 / 1024 )
                create_time = datetime.datetime.fromtimestamp(filedict["timestamp"])

                # Cleaning up the MassIVE in the file path
                filename = filename[13:]

                usi = "mzspec:{}:{}".format(dataset_accession, filename)

                collection_name, is_update, update_name =  _get_file_metadata(filename)

                fileinformation_dict = {}
                fileinformation_dict["usi"] = usi
                fileinformation_dict["dataset"] = dataset_accession
                fileinformation_dict["filepath"] = filename
                fileinformation_dict["sample_type"] = sample_type
                fileinformation_dict["collection"] = collection_name
                fileinformation_dict["is_update"] = is_update
                fileinformation_dict["update_name"] = update_name
                fileinformation_dict["create_time"] = create_time
                fileinformation_dict["size"] = size
                fileinformation_dict["size_mb"] = size_mb

                all_files_information.append(fileinformation_dict)


            except:
                pass
    
    # Writing out the file
    file_information_df = pd.DataFrame(all_files_information)
    file_information_df.to_csv(args.output_path, index=False, sep="\t")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path to the output TSV file.')
    parser.add_argument('--existing_datasets', type=str, default=None, help='Path to the existing datasets file.')
        
    args = parser.parse_args()
    main(args)
