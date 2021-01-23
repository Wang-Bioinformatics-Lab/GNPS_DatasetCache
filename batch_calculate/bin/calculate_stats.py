import sys
import json
import utils
import argparse
import uuid
import werkzeug
import os

parser = argparse.ArgumentParser(description='')
parser.add_argument("full_path")
parser.add_argument("input_filename")
parser.add_argument("msaccess_bin")
parser.add_argument("--output_json", default=None)

args = parser.parse_args()


output_image = werkzeug.utils.secure_filename(args.full_path) + ".png"
output_summary_scans = werkzeug.utils.secure_filename(args.full_path) + ".tsv"
output_filename = werkzeug.utils.secure_filename(args.full_path) + ".json"

if args.output_json is not None:
    output_filename = args.output_json

# Producing output
utils._calculate_image(args.input_filename, output_image, msaccess_path=args.msaccess_bin)
summary_scans_df = utils._calculate_file_scanslist(args.input_filename, output_summary_scans, msaccess_path=args.msaccess_bin)
run_metadata = utils._calculate_file_metadata(args.input_filename, msaccess_path=args.msaccess_bin)


summary_dict = utils._calculate_file_stats(args.input_filename, msaccess_path=args.msaccess_bin)
summary_dict["filename"] = args.full_path
summary_dict["png_filename"] = os.path.basename(output_image)
summary_dict["scans_filename"] = os.path.basename(output_summary_scans)
summary_dict["run_metadata"] = run_metadata

with open(output_filename, 'w') as o:
    o.write(json.dumps(summary_dict))

