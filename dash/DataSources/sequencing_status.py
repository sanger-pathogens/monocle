import json
import logging
import pandas
from   pandas import DataFrame, read_csv
import urllib.parse
import urllib.request
import yaml

# class DataSourceParamError(Exception):
#    """ exception when data source methods are called with invalid parameter(s) """
#    pass

class SequencingStatus:
   """ provides access to pipeline status data """
   
   def __init__(self, set_up=True):
      if set_up:
         self.set_up()
      
   def set_up(self):
      self.mlwh_client = MLWH_Client()
      
   def get_sample(self, sample_id):
      result = self.mlwh_client.find_by_id(sample_id)
      logging.debug("{}.get_sample({}) result(s) = {}".format(__class__.__name__,sample_id,result))
      # there should be one sample only
      return result

   def get_multiple_samples(self, sample_ids):
      """
      Pass a list of sample IDs.
      Returns a dict, keys are sample IDs, values are the sequencing status data as a dict
      If a sample ID is passed that is not found by the API, it will be missing from the returned dict.
      """
      results_list = self.mlwh_client.find_by_ids(sample_ids)
      logging.info("{}.get_multiple_samples() got {} result(s)".format(__class__.__name__,len(results_list)))
      # turn results list into dict keys on the sample IDs
      results_by_sample_id = {}
      for this_result in results_list:
         results_by_sample_id[ this_result.pop('id') ] = this_result
      return results_by_sample_id

class ProtocolError(Exception):
    pass

class MLWH_Client:
   
   data_sources_config     = 'data_sources.yml'
   data_source             = 'mlwh_rest_api'
   required_config_params  = [   'base_url',
                                 'swagger',
                                 'findById',
                                 'findById_key',
                                 'findByIds',
                                 'findByIds_key'
                                 ]
   def __init__(self, set_up=True):
      if set_up:
         self.set_up(self.data_sources_config)

   def set_up(self, config_file_name):
      with open(config_file_name, 'r') as file:
         data_sources = yaml.load(file, Loader=yaml.FullLoader)
         self.config  = data_sources[self.data_source]
      for required_param in self.required_config_params:
         if not required_param in self.config:
            logging.error("data source config file {} does not provide the required paramter {}.{}".format(self.data_sources_config,self.data_source,required_param))
            raise KeyError
      
   def find_by_id(self, sample_id):
      endpoint = self.config['findById']+sample_id
      logging.debug("{}.find_by_id({}) using endpoint {}".format(__class__.__name__,sample_id,endpoint))
      results = self.make_request(  endpoint,
                                    required_keys  = [self.config['findById_key']],
                                    )
      logging.debug("{}.find_by_id({}) returned {}".format(__class__.__name__,sample_id,results))
      return results[self.config['findById_key']]
   
   def find_by_ids(self, sample_ids):
      endpoint    = self.config['findByIds']
      logging.debug("{}.find_by_ids() using endpoint {}, passing list of {} sample IDs".format(__class__.__name__,endpoint,len(sample_ids)))
      results = self.make_request(  endpoint,
                                    post_data      = sample_ids,
                                    required_keys  = [self.config['findByIds_key']],
                                    )
      return results[self.config['findByIds_key']]

   def make_request(self, endpoint, post_data=None, required_keys=[]):
      request_url       = self.config['base_url']+endpoint
      swagger_url       = self.config['base_url']+self.config['swagger'] # only because it may be useful for error messages
      request_data      = None
      request_headers   = {}
      # if POST data were passed, convert to a UTF-8 JSON string
      if post_data is not None:
         assert ( isinstance(post_data, dict) or isinstance(post_data, list) ), "{}.make_request() requires post_data as a dict or a list, not {}".format(__class__.__name__,post_data)
         request_data = str(json.dumps(post_data))
         logging.debug("POST data for MLWH API: {}".format(request_data))
         request_data      = request_data.encode('utf-8')
         request_headers   = {'Content-type': 'application/json;charset=utf-8'}
      try:
         logging.info("request to MLWH API: {}".format(request_url))
         http_request = urllib.request.Request(request_url, data = request_data, headers = request_headers)
         with urllib.request.urlopen( http_request ) as this_response:
            response_as_string = this_response.read().decode('utf-8')
            logging.debug("response from MLWH API: {}".format(response_as_string))
            results_data = json.loads(response_as_string)
            if not isinstance(results_data, dict):
               error_message = "request to '{}' did not return a dict as expected (see API documentation at {})".format(endpoint, swagger_url)
               raise ProtocolError(error_message)
            for required_key in required_keys:
               try:
                  results_data[required_key]
               except KeyError:
                  error_message = "response data did not contain the expected key '{}' (see API documentation at {})".format(required_key,swagger_url)
                  raise ProtocolError(error_message)
            return results_data

      except urllib.error.HTTPError:
         logging.error("HTTP error during MLWH API request {}".format(request_url))
         raise

      return data
