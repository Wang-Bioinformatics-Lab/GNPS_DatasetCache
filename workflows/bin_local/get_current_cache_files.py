
import pandas as pd
import argparse
import requests

def stream_to_disk(url, output_file):
    print("Streaming", url)
    # Send a GET request to the URL
    try:
        response = requests.get(url, stream=True)
    except:
        return 1
    
    # Check if the request was successful
    if response.status_code == 200:
        # Open the output file in binary write mode
        with open(output_file, 'wb') as file:
            # Stream the content in chunks
            for chunk in response.iter_content(chunk_size=1024):
                # Filter out keep-alive new chunks
                if chunk:
                    file.write(chunk)
        print(f"Data successfully streamed to {output_file}")
        return 0
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return 1

def _get_database_all_files(output_filename):
    url = "http://localhost:5236/datasette/database/filename.csv?_stream=on&_size=max"

    ret_code = stream_to_disk(url, output_filename)

    if ret_code != 0:
        # Using the local version first
        url = "http://gnps-datasetcache-datasette2:5234/datasette/database/filename.csv?_stream=on&_size=max"

        ret_code = stream_to_disk(url, output_filename)

    if ret_code != 0:
        # We get the global version
        url = "http://datasetcachedatasette.gnps2.org/datasette/database/filename.csv?_stream=on&_size=max"

        ret_code = stream_to_disk(url, output_filename)

def _get_database_unique_mri(output_filename):
    url = "http://localhost:5236/datasette/database/uniquemri.csv?_stream=on&_size=max"

    ret_code = stream_to_disk(url, output_filename)

    if ret_code != 0:
        # Using the local version first
        url = "http://gnps-datasetcache-datasette2:5234/datasette/database/uniquemri.csv?_stream=on&_size=max"

        ret_code = stream_to_disk(url, output_filename)

    if ret_code != 0:
        # We get the global version
        url = "http://datasetcachedatasette.gnps2.org/datasette/database/uniquemri.csv?_stream=on&_size=max"

        ret_code = stream_to_disk(url, output_filename)


def main():
    # argparse
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('output_dataset_filename', type=str, help='Path to the output CSV file.')
    parser.add_argument('output_unique_mri_filename', type=str, help='Path to the output CSV file.')
    
    args = parser.parse_args()

    # Processing the output
    _get_database_all_files(args.output_dataset_filename)
    _get_database_unique_mri(args.output_unique_mri_filename)


if __name__ == "__main__":
    main()
