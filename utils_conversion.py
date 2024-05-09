import uuid
import os
import requests
import glob

CONVERSION_STAGING_FOLDER = "temp/conversion_staging"
CONVERSION_RESULT_FOLDER =  "temp/conversion_output"

def determine_mri_path(mri):
    mri_hash = str(uuid.uuid3(uuid.NAMESPACE_DNS, mri))
    prefix_hash = mri_hash[:2]

    conversion_filefolder = os.path.join(prefix_hash, mri_hash)

    return conversion_filefolder

def status_mri(mri):
    # We are going to check if the file is present, true or false

    conversion_hashed_path = determine_mri_path(mri)
    
    conversion_folder = os.path.join(CONVERSION_RESULT_FOLDER, conversion_hashed_path)

    # lets see if there is an mzML file in that folder
    mzml_files = glob.glob(os.path.join(conversion_folder, "*.mzML"))

    if len(mzml_files) > 0:
        return True

    return False


def download_mri(mri, conversion_cache_folder, cache_url="https://datasetcache.gnps2.org"):
    conversion_folder = conversion_cache_folder

    # lets get the extension of the filename
    mri_splits = mri.split(":")
    
    dataset_accession = mri_splits[1]

    filename = mri_splits[2]
    # if starts with MSV
    if dataset_accession.startswith("MSV"):
        if not filename.startswith(dataset_accession):
            filename = os.path.join(dataset_accession, filename)

    raw_filename = os.path.basename(filename)
    extension = filename.split(".")[-1]

    path_to_full_raw_filename = os.path.join(conversion_folder, raw_filename)

    print(extension, "extension")

    if extension == "d":
        # We need to go to the dataset cache and grab all the files
        #https://datasetcache.gnps2.org/datasette/datasette/database/filename.json?_sort=usi&dataset__exact=MSV000093337&filepath__startswith=MSV000093337%2Fccms_parameters%2Fparams.xml
        params = {}
        params["_shape"] = "array"
        params["dataset__exact"] = mri_splits[1]
        params["filepath__startswith"] = filename

        url =  "{}/datasette/datasette/database/filename.json".format(cache_url)

        r = requests.get(url, params=params)

        if r.status_code == 200:
            # lets get all he files
            file_rows = r.json()

            for file_row in file_rows:
                print("FILE ROW", file_row)

                mri_specific_usi = file_row["usi"]
                mri_specific_filepath = file_row["filepath"]

                # file relative file path to original filename
                relative_filepath = os.path.relpath(mri_specific_filepath, filename)
                target_specific_filepath = os.path.join(conversion_folder, raw_filename, relative_filepath)

                os.makedirs(os.path.dirname(target_specific_filepath), exist_ok=True)

                # HACK TODO: fix MSV in filepath 
                if mri_specific_filepath.startswith("MSV"):
                    # splitting the mri
                    mri_specific_splits = mri_specific_usi.split(":")
                    mri_specific_usi = mri_specific_splits[0] + ":" + mri_specific_splits[1] + ":" + mri_specific_splits[2][13:]


                # Now we need to figure out how to get this file given the MRI
                url = "https://dashboard.gnps2.org/downloadlink"
                params = {}
                params["usi"] = mri_specific_usi

                print("GETTING Dashboard Download link")

                r = requests.get(url, params=params)

                # This gives us the download
                if r.status_code == 200:
                    download_url = r.text

                    print("DOWNLOAD LINK", download_url)

                    r = requests.get(download_url)

                    if r.status_code == 200:
                        with open(target_specific_filepath, "wb") as f:
                            f.write(r.content)
                    else:
                        import sys
                        print("Error downloading", download_url, file=sys.stderr)

    return path_to_full_raw_filename

def convert_mri(raw_filename, output_conversion_folder):
    extension = raw_filename.split(".")[-1]

    cmd = None

    """Bruker Conversion"""
    if extension == "d":
        output_filename = os.path.basename(raw_filename).replace(".d", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (raw_filename, output_conversion_folder, output_filename)

    """Thermo Conversion"""
    if extension == "raw":
        output_filename = os.path.basename(raw_filename).replace(".raw", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (raw_filename, output_conversion_folder, output_filename)

    """Sciex Conversion"""
    if extension == "wiff":
        output_filename = os.path.basename(raw_filename).replace(".wiff", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (raw_filename, output_conversion_folder, output_filename)

    os.system(cmd)