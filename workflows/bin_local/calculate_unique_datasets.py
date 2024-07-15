import pandas as pd
import os
import argparse
import requests
import time

def main(args):

    # retry up to 5 times
    retries = 5
    wait_time = 30

    for attempt in range(retries):
        try:
            url = "https://datasetcache.gnps2.org/datasette/database.json?sql=SELECT+DISTINCT+dataset%0D%0AFROM+filename%3B"
            r = requests.get(url, timeout=60)

            all_datasets_list = r.json()["rows"]

            # unrolling the dataset from a embedded list
            all_datasets = []
            for dataset in all_datasets_list:
                all_datasets.append(dataset[0])


            df = pd.DataFrame()
            df["datasets"] = all_datasets

            df.to_csv(args.output_path, sep="\t", index=False)

            exit(0)
        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("All retry attempts failed.")
                
    # Writing out empty file with dataset column header
    with open(args.output_path, 'w') as f:
        f.write('dataset\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path to the output TSV file.')
    args = parser.parse_args()
    main(args)
