import pandas as pd
import os
import argparse

def main(args):
    try:
        df = pd.read_csv(args.input_path, low_memory=False)

        # get only dataset column and unique
        all_datasets = list(set(df['dataset']))

        df_datasets = pd.DataFrame(all_datasets, columns=['dataset'])

        # save to tsv
        df_datasets.to_csv(args.output_path, sep='\t', index=False)

        exit(0)
    except FileNotFoundError:
        print("Error: File not found!")
    except pd.errors.ParserError:
        print("Error: Could not parse the CSV file.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Writing out empty file with dataset column header
    with open(args.output_path, 'w') as f:
        f.write('dataset\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('-i', '--input_path', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path to the output TSV file.')
    args = parser.parse_args()
    main(args)
