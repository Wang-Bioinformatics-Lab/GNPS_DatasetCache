
import os
import sys
import pandas as pd
import argparse
from pathlib import Path

# Extract MRIs with sample_type GNPS, MTBLS, MWB and ends with mzML/mzml or mzXML/mzxml
# Allowed sample types and file extensions
allowed_sample_types = {'GNPS', 'MTBLS', 'MWB'}
#allowed_extensions = {'.mzXML', '.mzML', '.mzml', '.mzxml'}


def main():
    # argparse
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('input_mri_list', type=str, help='Path to the input CSV file.')
    parser.add_argument('output_filtered_mri_list', type=str, help='Path to the output CSV file.')
    
    args = parser.parse_args()

    # reading the input data
    df = pd.read_csv(args.input_mri_list, sep="\t")

    download_mri_df = filter_mri(df)

    # Keeping only usi column 
    download_mri_df = download_mri_df[['usi']]

    # Saving output
    download_mri_df.to_csv(args.output_filtered_mri_list, sep="\t", index=False)


def filter_mri(input_mri_df):
    df = input_mri_df

    # Filtering to mzML and mzXML extensiosn
    df = df[df['usi'].str.endswith(('.mzML', '.mzml', '.mzXML', '.mzxml'))]

    return df


if __name__ == "__main__":
    main()
