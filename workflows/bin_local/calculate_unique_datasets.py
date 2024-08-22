import pandas as pd
import os
import argparse
import requests
import time

def main(args):

    # Reading the input
    all_files_df = pd.read_csv(args.input_path, sep=",")

    # Getting unique datasets
    all_datasets = all_files_df["dataset"].unique()

    # Writing out the unique datasets
    df = pd.DataFrame()
    df["datasets"] = all_datasets

    df.to_csv(args.output_path, sep="\t", index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    
    parser.add_argument('--input_path', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output_path', type=str, required=True, help='Path to the output TSV file.')

    args = parser.parse_args()
    
    main(args)
