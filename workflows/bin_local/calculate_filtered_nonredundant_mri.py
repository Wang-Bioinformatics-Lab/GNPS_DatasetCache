
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
    parser.add_argument('output_removed_mri_list', type=str, help='Path to the output CSV file.')
    
    args = parser.parse_args()

    # reading the input data
    df = pd.read_csv(args.input_mri_list, sep="\t")

    filtered_selected_df, filtered_removed_df = filter_mri(df)

    # Saving output
    filtered_selected_df.to_csv(args.output_filtered_mri_list, sep="\t", index=False)
    filtered_removed_df.to_csv(args.output_removed_mri_list, sep="\t", index=False)


def filter_mri(input_mri_df):
    df = input_mri_df

    # Filtering __MACOSX
    df = df[~df['usi'].str.contains(":__MACOSX")]

    # Filtering the allowed_sample_types
    df = df[df['sample_type'].isin(allowed_sample_types)]

    # Filtering the allowed_extensions
    #df = df[df['usi'].str.endswith(tuple(allowed_extensions))]

    # Now we are doing the hard part, we want to make sure that we are only keeping one file per dataset
    filtered_selected_df, filtered_removed_df = filter_redundant_files(df)

    return filtered_selected_df, filtered_removed_df

def filter_redundant_files(input_df):
    grouped_by_dataset = input_df.groupby("dataset")

    selected_list = []
    removed_list = []

    for dataset, group_df in grouped_by_dataset:
        #print(dataset, len(group_df))
        #print(group_df)

        # remove extension
        group_df["extension"] = group_df["usi"].apply(lambda x: os.path.splitext(x)[-1])
        group_df["cleanedfilepath"] = group_df["filepath"].apply(lambda x: os.path.splitext(x)[0])

        # stripping off first folder using path
        group_df["cleanedfilepath"] = group_df["cleanedfilepath"].apply(lambda x: "/".join(Path(x).parts[1:]))

        # Stripping off full path
        group_df["cleanedfilename"] = group_df["cleanedfilepath"].apply(lambda x: os.path.basename(x))



        # Determining a score for what we want to choose
        group_df["score"] = 0.0

        # If the file is mzML, we want to add 1
        group_df.loc[group_df['extension'] == ".mzML", "score"] += 1.0

        # If the file is mzXML, we want to add .5
        group_df.loc[group_df['extension'] == ".mzXML", "score"] += 0.5

        # Count number of unique in cleaned path
        number_of_uniquepath = group_df["cleanedfilepath"].nunique()
        number_of_files = len(group_df)
        number_of_uniquefilename = group_df["cleanedfilename"].nunique()


        if "MSV" in dataset:
            print("MSV", dataset)

            group_df["collection"] = group_df["filepath"].apply(lambda x: Path(x).parts[0])

            
            # If the file is ccms_peak collection
            group_df.loc[group_df['collection'] == "ccms_peak", "score"] += 1.0

            if number_of_uniquefilename != number_of_files:
                # sorting by score
                group_df = group_df.sort_values("score", ascending=False)

                group_df["selected"] = 0

                json_object_list = group_df.to_dict(orient="records")

                # Iterative selecting and removing objects
                for json_object in json_object_list:
                    if json_object["selected"] == 0:
                        selected_list.append(json_object)
                        json_object["selected"] = 1

                        current_collection = json_object["collection"]
                        current_cleanedfilename = json_object["cleanedfilename"]

                        # Now we need to remove all other files that have the same cleanedfilename and different collections
                        for json_object2 in json_object_list:
                            if json_object2["cleanedfilename"] == current_cleanedfilename and json_object2["collection"] != current_collection:
                                if json_object2["selected"] != 1:
                                    removed_list.append(json_object2)
                                    json_object2["selected"] = 1
            else:
                # there is no duplication in filenames
                selected_list += group_df.to_dict(orient="records")

        else:
            # We are not dealing with an MSV dataset, lets not consider collection, lets just consider the filename themselves
            # sorting by score
            group_df = group_df.sort_values("score", ascending=False)

            group_df["selected"] = 0

            json_object_list = group_df.to_dict(orient="records")

            # Iterative selecting and removing objects
            for json_object in json_object_list:
                if json_object["selected"] == 0:
                    selected_list.append(json_object)
                    json_object["selected"] = 1

                    current_cleanedfilename = json_object["cleanedfilename"]

                    # Now we need to remove all other files that have the same cleanedfilename and different collections
                    for json_object2 in json_object_list:
                        if json_object2["cleanedfilename"] == current_cleanedfilename:
                            if json_object2["selected"] != 1:
                                removed_list.append(json_object2)
                                json_object2["selected"] = 1

    filtered_selected_df = pd.DataFrame(selected_list)
    filtered_removed_df = pd.DataFrame(removed_list)

    return filtered_selected_df, filtered_removed_df

if __name__ == "__main__":
    main()
