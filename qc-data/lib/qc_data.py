#!/usr/bin/env python3

import os.path
import json

class QCData:

    def __init__(self, file_path, setUp = True):
        self.file_path = file_path
        if setUp:
            self.setup()


    def setup(self):
        if os.path.exists(self.file_path):
            f = open(self.file_path)
            self.qc_data = json.load(f)
            f.close()
        else:
            self.qc_data = {}


    def get_data(self):
        return self.qc_data


    def update(self, qc_metric, qc_info):
        """Reads the qc data in the qc data json file and returns updated qc data dictionary"""

        if qc_metric in self.qc_data:
            existing_vals = [item['value'] for item in self.qc_data[qc_metric]]
            if qc_info['value'] not in existing_vals:
                self.qc_data[qc_metric].append(qc_info)
        else:
            self.qc_data[qc_metric] = [qc_info]


    def write_file(self):
        """Overwrites file with updated qc data"""

        with open(self.file_path, 'w') as outfile:
            json_object = json.dumps(self.qc_data)
            outfile.write(json_object)
