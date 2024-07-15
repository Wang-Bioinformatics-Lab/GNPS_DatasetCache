import pandas as pd
import os
import argparse
import requests

def _get_dataset_files(dataset):
    return None

def _get_all_datasets():
    return []

def main(args):
    print(args)

    # Getting all GNPS Datasets

    # Getting each ones' files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('-i', '--input_path', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path to the output TSV file.')
    args = parser.parse_args()
    main(args)
