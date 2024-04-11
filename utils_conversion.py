import uuid
import os
import requests

def download_mri(mri, conversion_cache_folder):
    mangled_string = str(uuid.uuid4())

    conversion_folder = os.path.join(conversion_cache_folder, mangled_string)

    # lets get the extension of the filename
    mri_splits = mri.split(":")

    filename = mri_splits[2]
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

        url =  "https://datasetcache.gnps2.org/datasette/datasette/database/filename.json"

        r = requests.get(url, params=params)

        if r.status_code == 200:
            # lets get all he files
            file_rows = r.json()

            for file_row in file_rows:
                print(file_row)

                mri_specific_usi = file_row["usi"]
                mri_specific_filepath = file_row["filepath"]

                # file relative file path to original filename
                relative_filepath = os.path.relpath(mri_specific_filepath, filename)
                target_specific_filepath = os.path.join(conversion_folder, raw_filename, relative_filepath)

                os.makedirs(os.path.dirname(target_specific_filepath), exist_ok=True)

                # Now we need to figure out how to get this file given the MRI
                url = "https://dashboard.gnps2.org/downloadlink"
                params = {}
                params["usi"] = mri_specific_usi

                r = requests.get(url, params=params)

                with open(target_specific_filepath, "wb") as f:
                    f.write(r.content)

    return path_to_full_raw_filename

def convert_mri(raw_filename, output_conversion_folder):
    extension = raw_filename.split(".")[-1]

    cmd = None

    """Bruker Conversion"""
    for extension == "d":
        output_filename = os.path.basename(raw_filename).replace(".d", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (raw_filename, output_conversion_folder, output_filename)

    """Thermo Conversion"""
    for extension == "raw":
        output_filename = os.path.basename(raw_filename).replace(".raw", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (raw_filename, output_conversion_folder, output_filename)

    """Sciex Conversion"""
    for extension == "wiff":
        output_filename = os.path.basename(raw_filename).replace(".wiff", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (raw_filename, output_conversion_folder, output_filename)

    os.system(cmd)