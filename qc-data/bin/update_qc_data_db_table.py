import argparse
import http.client
import json
import logging
import os.path
import sys
#import urllib.parse
import urllib.request
import yaml


qc_data_file_name       = 'qc_data.json'
qc_data_file_min_size   = 3 # files smaller than this assumed to be empty

#QC data inclues a `rel_abundance` value, which is a list of the values for each species.
#In the Monocle db have field(s) with relative abundance for specific species.
#This dict maps the species name (i.e. as found in the original QC data) on to the parameter
#used in the QC data upload to the database (i.e. as found in the OpenAPI spec. for the
#/qc_data_upload endpoint)
rel_abun_species        = {'Streptococcus agalactiae': 'rel_abun_sa'}

# API config details
data_sources_config     = '/app/data_sources.yml'
data_source             = 'monocle_metadata_api'
required_config_params  = [   'base_url',
                              'qc_data_upload',
                              'qc_data_delete_all'
                              ]



def get_api_config():
    with open(data_sources_config, 'r') as config_file:
       data_sources = yaml.load(config_file, Loader=yaml.FullLoader)
       config = data_sources[data_source]
    for required_param in required_config_params:
       if not required_param in config:
             logging.error("data source config file {} does not provide the required paramter {}.{}".format(
                data_sources_config, data_source, required_param))
             raise KeyError
    return config

def _make_request(request_url, post_data=None):
    request_data = None
    request_headers = {}
    # if POST data were passed, convert to a UTF-8 JSON string
    if post_data is not None:
       assert (isinstance(post_data, dict) or isinstance(post_data, list)), "{}.make_request() requires post_data as a dict or a list, not {}".format(class__.__name__, post_data)
       request_data = str(json.dumps(post_data))
       logging.debug("POST data for Metadata API: {}".format(request_data))
       request_data = request_data.encode('utf-8')
       request_headers = {'Content-type': 'application/json;charset=utf-8'}
    try:
       logging.info("Making request to Metadata API: {}".format(request_url))
       logging.debug("Request to metadata API:\n\tURL = {}\n\theaders = {}\n\tPOST data = {}".format(request_url,request_headers,request_data))
       http_request = urllib.request.Request(request_url, data=request_data, headers=request_headers)
       with urllib.request.urlopen(http_request) as this_response:
         response_as_string = this_response.read().decode('utf-8')
         logging.debug("response from Metadata API: {}".format(response_as_string))
    except urllib.error.HTTPError:
       logging.error("HTTP error during Metadata API request {}".format(request_url))
       raise
    return response_as_string

def _find_files(name, path):
    result = []
    for root, dirs, files in os.walk(path):
       if name in files:
          result.append(os.path.join(root, name))
    return result

def _get_qc_data(qc_dir):
    logging.info("Looking in {} to get QC data".format(qc_dir))
    qc_data = []
    
    for this_file in _find_files(qc_data_file_name, qc_dir):
       if os.path.getsize(this_file) >= qc_data_file_min_size:
          logging.debug("Looking at QC data file {}".format(this_file))
          with open(this_file, "r") as this_file_read:
             qc_data.append({ 'lane_id': os.path.basename(os.path.dirname(this_file)),
                              'qc_data': json.load(this_file_read)
                              })
    logging.info("Found {} files with QC data".format(len(qc_data)))
    logging.debug("Complete QC data read:\n{}".format(qc_data))
    
    return qc_data
 
def _get_update_request_body(qc_dir):
    qc_data = _get_qc_data(qc_dir)

    request_data = []
    for this_lane in qc_data:
       lane_id = this_lane['lane_id']
       qc_data = this_lane['qc_data']
       # construct a dict with request data for this lane
       this_lane_request_data = {'lane_id': lane_id}
       for this_rel_abundance in qc_data.get('rel_abundance', []):
          this_species  = this_rel_abundance['species']
          this_value    = float(this_rel_abundance['value'])
          if this_species in rel_abun_species:
             request_property = rel_abun_species[this_species]
             logging.debug("{} has rel abubndance {}; adding to request as property {}".format(this_species,this_value,request_property))
             this_lane_request_data[request_property] = this_value
       # add request data to array with data for all lanes
       request_data.append(this_lane_request_data)
       
    return request_data

def update_database(qc_dir, api_config):
    request_data = _get_update_request_body(qc_dir)
    request_url = api_config['base_url'] + api_config['qc_data_upload']
    logging.info("Updating QC data for {} lanes".format(len(request_data)))
    _make_request(request_url, post_data=request_data)
   
def delete_qc_data_from_database(api_config):
    request_url = api_config['base_url'] + api_config['qc_data_delete_all']
    logging.info("Deleting QC data from database")
    _make_request(request_url)

def get_arguments():
    parser = argparse.ArgumentParser(description='Update QC data in Monocle database')
    default_qc_data_path = os.environ.get('MONOCLE_PIPELINE_QC_DATA', '/app/monocle_pipeline_qc')
    default_log_level='WARNING'
    parser.add_argument("-D", "--pipeline_qc_dir",
                        help="Pipeline QC data root directory [default: {}]; can set with MONOCLE_PIPELINE_QC_DATA environment variable".format(default_qc_data_path),
                        default=default_qc_data_path
                        )
    parser.add_argument("-L", "--log_level",
                        help="Logging level [default: {}]".format(default_log_level),
                        choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'],
                        default=default_log_level
                        )
    return parser

def main():
    parser = get_arguments()
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)-15s %(levelname)s %(module)s:  %(message)s', level=args.log_level)
    api_config = get_api_config()
    delete_qc_data_from_database(api_config)
    update_database(args.pipeline_qc_dir, api_config)

if __name__ == '__main__':
   sys.exit(main())
