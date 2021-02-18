import requests
import pandas as pd
import sys
import os

input_dump = sys.argv[1]

df = pd.read_csv(input_dump, sep=",")

# Filtering to mzML/mzXML
df["extension"] = df["filepath"].apply(lambda x: os.path.splitext(x)[-1])
df = df[df["extension"].isin([".mzML", ".mzXML"])]
df = df[df["file_processed"] != "FAILED"]
print(df)


# Getting GNPS Output
gnps_df = df[df["sample_type"] == "GNPS"]
gnps_save_df = gnps_df[["filepath", "dataset", "collection", "create_time", "size", "size_mb", "spectra_ms1", "spectra_ms2", "instrument_vendor", "instrument_model", "extension"]]
gnps_save_df.to_csv("gnps_public_openformats.tsv", sep="\t", index=False)

# Getting MassIVE Output
massive_save_df = df[["filepath", "dataset", "collection", "create_time", "size", "size_mb", "spectra_ms1", "spectra_ms2", "instrument_vendor", "instrument_model", "extension"]]
massive_save_df.to_csv("massive_public_openformats.tsv", sep="\t", index=False)

