import pandas as pd
import os
import argparse

def prefer_extension(group):
    mask = group['extension'].isin(['mzml', 'mzxml'])
    if mask.any():
        group['keep'] = mask
    else:
        group['keep'] = [True] + [False] * (len(group) - 1)
    return group

def filter_usi_extensions(df):
    allowed_extensions = ["mzml", "mzxml", "raw", "d"]
    df['filename'] = df['filepath'].apply(lambda x: os.path.basename(x))
    df[['base', 'extension']] = df['filename'].str.rsplit('.', n=1, expand=True)
    df['extension'] = df['extension'].str.lower()
    df = df[df['extension'].isin(allowed_extensions)]
    df = df.groupby(['dataset', 'base'], as_index=False).apply(prefer_extension)
    df = df[df['keep']]
    return df.drop(columns=['filename', 'base', 'extension', 'keep'])

def main(args):
    try:
        df = pd.read_csv(args.input_path, low_memory=False)
        df_filtered = filter_usi_extensions(df)
        df_filtered.to_csv(args.output_path, index=False)
        print(f"Processed file saved to {args.output_path}")
    except FileNotFoundError:
        print("Error: File not found!")
    except pd.errors.ParserError:
        print("Error: Could not parse the CSV file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter files based on extensions and preferences.")
    parser.add_argument('-i', '--input_path', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path to the output CSV file.')
    args = parser.parse_args()
    main(args)
