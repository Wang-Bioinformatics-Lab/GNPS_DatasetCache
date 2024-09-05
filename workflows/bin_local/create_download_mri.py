
import os
import sys
import pandas as pd
import argparse
from pathlib import Path
import pytrie
from tqdm import tqdm


# Extract MRIs with sample_type GNPS, MTBLS, MWB and ends with mzML/mzml or mzXML/mzxml
# Allowed sample types and file extensions
allowed_sample_types = {'GNPS', 'MTBLS', 'MWB'}
#allowed_extensions = {'.mzXML', '.mzML', '.mzml', '.mzxml'}


def main():
    # argparse
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('input_nonredundant_mri_list', type=str, help='Path to the input TSV file.')
    parser.add_argument('input_full_mri_list', type=str, help='Path to the input CSV file.')
    parser.add_argument('output_filtered_mri_list', type=str, help='Path to the output CSV for only mzML/mzXML files')
    parser.add_argument('output_thermoraw_mri_list', type=str, help='Path to thermo raw files')
    
    args = parser.parse_args()

    # reading the input data
    df = pd.read_csv(args.input_nonredundant_mri_list, sep="\t")

    download_mri_df = filter_mri(df)

    # Keeping only usi column 
    download_mri_df = download_mri_df[['usi']]

    # Saving output
    download_mri_df.to_csv(args.output_filtered_mri_list, sep="\t", index=False)

    # Finding the unkept files
    unkept_files_df = df[~df['usi'].isin(download_mri_df['usi'])]
    raw_files_df = unkept_files_df[unkept_files_df['usi'].str.endswith('.raw')]

    print("BEFORE", len(raw_files_df))

    filtered_raw_files_df = filter_thermoraw_mri(raw_files_df, args.input_full_mri_list)

    print("FILTERED", len(filtered_raw_files_df))

    # Saving output for thermo raw
    filtered_raw_files_df.to_csv(args.output_thermoraw_mri_list, sep="\t", index=False)

    
def filter_thermoraw_mri(raw_files_df, input_full_mri_list):
    # keep only the usi column when reading
    all_mri_df = pd.read_csv(input_full_mri_list, engine="pyarrow", usecols=['usi'])

    # Getting the usi
    usi_list = all_mri_df['usi'].tolist()

    # getting usi list only if ".raw" is in the usi
    usi_list = [usi for usi in usi_list if ".raw" in usi]

    # lets create a trie
    print("Creating trie")
    trie = pytrie.StringTrie()
    for string in tqdm(usi_list):
        trie[string] = True

    print("Searching the trie")
    # Searching the trie
    all_unique_raw_usi = raw_files_df['usi'].unique()
    kept_raw_usi = []
    for raw_usi in tqdm(all_unique_raw_usi):
        raw_usi
        #print('PREFIX', prefix)
        if raw_usi in trie:
            #print("FOUND", prefix)
            #print("FOUND", sum(1 for _ in trie.iterkeys(raw_usi)))
            # output when it is found

            all_found = list(trie.iterkeys(raw_usi))
            #print(raw_usi)
            #print(all_found)

            if len(all_found) == 1:
                kept_raw_usi.append(raw_usi)

        else:
            print("NOT FOUND", raw_usi)

    # Filtering down the input dataframe
    kept_raw_usi = set(kept_raw_usi)
    filtered_raw_files_df = raw_files_df[raw_files_df['usi'].isin(kept_raw_usi)]

    return filtered_raw_files_df





def filter_mri(input_mri_df, extensions=[".mzML", ".mzml", ".mzXML", ".mzxml"]):
    df = input_mri_df

    # Filtering to mzML and mzXML extension
    df = df[df['usi'].str.endswith(tuple(extensions))]

    return df


if __name__ == "__main__":
    main()
