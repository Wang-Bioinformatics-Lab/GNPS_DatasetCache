
import os
import sys
import pandas as pd
import argparse

# Extract MRIs with sample_type GNPS, MTBLS, MWB and ends with mzML/mzml or mzXML/mzxml
# Allowed sample types and file extensions
allowed_sample_types = {'GNPS', 'MTBLS', 'MWB'}
allowed_extensions = {'.mzXML', '.mzML', '.mzml', '.mzxml'}


def main():
    # argparse
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('input_mri_list', type=str, help='Path to the input CSV file.')
    parser.add_argument('output_filtered_mri_list', type=str, help='Path to the input CSV file.')
    
    args = parser.parse_args()

    # reading the input data
    df = pd.read_csv(args.input_mri_list, sep=",")

    filtered_df = filter_mri(df)

    # Saving output
    filtered_df.to_csv(args.output_filtered_mri_list, sep="\t", index=False)


def filter_mri(input_mri_df):
    # Filtering __MACOSX
    df = df[~df['usi'].str.contains(":__MACOSX")]

    # Filtering the allowed_sample_types
    df = df[df['sample_type'].isin(allowed_sample_types)]

    # Filtering the allowed_extensions
    df = df[df['usi'].str.endswith(tuple(allowed_extensions))]

    return df

if __name__ == "__main__":
    main()
