
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

    print(len(raw_files_df))

    filter_thermoraw_mri(raw_files_df, args.input_full_mri_list)

    
def filter_thermoraw_mri(input_mri_df, input_full_mri_list):
    all_mri_df = pd.read_csv(input_full_mri_list, engine="pyarrow")
    # Getting the usi
    usi_list = input_mri_df['usi'].tolist()

    # lets create a trie
    print("Creating trie")
    trie = pytrie.StringTrie()
    for string in tqdm(usi_list):
        trie[string] = True

    print("Searching the trie")
    # Searching the trie
    for index, row in tqdm(all_mri_df.iterrows()):
        prefix = row['usi']
        if prefix in trie:
            print("FOUND", sum(1 for _ in trie.iterkeys(prefix)))




def filter_mri(input_mri_df, extensions=[".mzML", ".mzml", ".mzXML", ".mzxml"]):
    df = input_mri_df

    # Filtering to mzML and mzXML extension
    df = df[df['usi'].str.endswith(tuple(extensions))]

    return df


if __name__ == "__main__":
    main()
