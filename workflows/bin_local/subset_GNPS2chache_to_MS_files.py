import pandas as pd
import os
import argparse


def clean_mac_path(path):
    if path.startswith("__MACOSX/") and '/._' in path:
        # Remove the __MACOSX part and the ._ prefix from the filename
        return path.replace("__MACOSX/", "").replace("/._", "/")
    return path


def prefer_extension(group):
    mask = group['extension'].isin(['mzml', 'mzxml'])
    if mask.any():
        group['keep'] = mask
    else:
        group['keep'] = [True] + [False] * (len(group) - 1)
    return group

def normalize_d_paths(path):
    if '.d' in path:
        parts = path.split('/')
        for i, part in enumerate(parts):
            if '.d' in part and part.endswith('.d'):
                return '/'.join(parts[:i+1])
    return path

def normalize_usi(usi, normalized_path):
    parts = usi.split(':')
    if len(parts) > 2:
        # Extract the path component from the USI
        path_parts = parts[2].split('/')
        # Find the first occurrence of a '.d' directory and normalize
        for i, part in enumerate(path_parts):
            if '.d' in part and part.endswith('.d'):
                path_parts = path_parts[:i+1]
                break
        # Reconstruct the USI with the normalized path
        parts[2] = '/'.join(path_parts)
        return ':'.join(parts)
    return usi

def filter_usi_extensions(df):
    allowed_extensions = ["mzml", "mzxml", "raw", "d"]
    df['filename'] = df['filepath'].apply(lambda x: os.path.basename(x))
    df['filepath'] = df['filepath'].apply(normalize_d_paths)
    df['usi'] = df.apply(lambda row: normalize_usi(row['usi'], row['filepath']), axis=1)
    df[['base', 'extension']] = df['filename'].str.rsplit('.', n=1, expand=True)
    df['extension'] = df['extension'].str.lower()
    df = df[df['extension'].isin(allowed_extensions)]
    df = df.groupby(['dataset', 'base'], as_index=False).apply(prefer_extension)
    df = df[df['keep']]
    return df.drop(columns=['filename', 'base', 'extension', 'keep']).drop_duplicates(subset=['usi'])

def main(args):
    try:
        df = pd.read_csv(args.input_path, low_memory=False)
        df['filename'] = df['filepath'].apply(lambda x: clean_mac_path(x))
        df['usi'] = df['usi'].apply(lambda x: clean_mac_path(x))
        df_filtered = filter_usi_extensions(df)
        df_filtered.to_csv(args.output_path, sep='\t', index=False)
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
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path to the output TSV file.')
    args = parser.parse_args()
    main(args)
