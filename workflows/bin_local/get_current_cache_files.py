
import pandas as pd
import argparse
import requests

def main():
    # argparse
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('output_dataset_filename', type=str, help='Path to the output CSV file.')
    
    args = parser.parse_args()

    # Using the local version first
    try:
        r = requests.get("http://gnps-datasetcache-datasette:5234/datasette/database/uniquemri.csv?_stream=on&_size=max")
        r.raise_for_status()
    except:
        # We get the global version
        r = requests.get("https://datasetcache.gnps2.org/datasette/database/uniquemri.csv?_stream=on&_size=max")

    with open(args.output_dataset_filename, "wb") as output_file:
        output_file.write(r.content)

    


if __name__ == "__main__":
    main()
