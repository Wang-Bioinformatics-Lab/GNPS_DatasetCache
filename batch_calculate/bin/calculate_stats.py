import sys
import json
import utils
import argparse
import uuid

parser = argparse.ArgumentParser(description='')
parser.add_argument("full_path")
parser.add_argument("input_filename")
parser.add_argument("msaccess_bin")
parser.add_argument("--output_json", default=None)

args = parser.parse_args()

summary_dict = utils._calculate_file_stats(args.input_filename, msaccess_path=args.msaccess_bin)
summary_dict["filename"] = args.full_path

output_filename = str(uuid.uuid4()) + ".json"

if args.output_json is not None:
    output_filename = args.output_json

with open(output_filename, 'w') as o:
    o.write(json.dumps(summary_dict))