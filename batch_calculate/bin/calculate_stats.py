import sys
import json
import utils


input_filename = sys.argv[1]
output_json = sys.argv[2]

summary_dict = utils._calculate_file_stats(input_filename)
with open(output_json, 'w') as o:
    o.write(json.dumps(output_json))