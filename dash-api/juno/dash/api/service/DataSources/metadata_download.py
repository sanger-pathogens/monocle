import http.client
import json
import logging
import urllib.parse
import urllib.request
import yaml

# run test metadata api server with:
# 
# IMAGE=gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-metadata:unstable
# docker run -p 8080:80 -v`pwd`/dash/my.cnf:/app/my.cnf -v`pwd`/metadata/juno/config.json:/app/config.json --env ENABLE_SWAGGER_UI=true --rm ${IMAGE}

class MetadataDownload:
   """ provides access to monocle metadata """
   
   def __init__(self, set_up=True):
      if set_up:
         self.set_up()
      
   def set_up(self):
      self.dl_client = Monocle_Download_Client()
            
   def get_metadata(self, lane_id_list):
      logging.debug("{}.get_metadata() called with {}".format(__class__.__name__,lane_id_list))
      results_list = self.dl_client.metadata(lane_id_list)
      assert ( isinstance(results_list, list) ), "Monocle_Download_Client.metadata() was expected to return a list, not {}".format(type(results_list))
      logging.debug("{}.get_metadata() result 1: {}".format(__class__.__name__,results_list[0]))
      logging.info("{}.get_metadata() got {} result(s)".format(__class__.__name__,len(results_list)))
      return results_list

   def get_in_silico_data(self, lane_id_list):
      logging.debug("{}.get_in_silico_data() called with {}".format(__class__.__name__,lane_id_list))
      results_list = self.dl_client.in_silico_data(lane_id_list)
      assert ( isinstance(results_list, list) ), "Monocle_Download_Client.in_silico_data() was expected to return a list, not {}".format(type(results_list))
      if len(results_list) > 0:
         logging.debug("{}.get_in_silico_data() result 1: {}".format(__class__.__name__,results_list[0]))
      logging.info("{}.get_in_silico_data() got {} result(s)".format(__class__.__name__,len(results_list)))
      return results_list

class ProtocolError(Exception):
    pass


class Monocle_Download_Client:
   
   data_sources_config     = 'data_sources.yml'
   data_source             = 'monocle_metadata_api'
   required_config_params  = [   'base_url',
                                 'swagger',
                                 'download',
                                 'metadata_key',
                                 'download_in_silico_data',
                                 'in_silico_data_key'
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
            logging.error("data source config file {} does not provide the required parameter {}.{}".format(self.data_sources_config,self.data_source,required_param))
            raise KeyError
      
   def metadata(self, lane_id_list):
      endpoint = self.config['download']
      logging.debug("{}.metadata() using endpoint {}, passing list of {} sample IDs".format(__class__.__name__,endpoint,len(lane_id_list)))
      response = self.make_request( endpoint, post_data = lane_id_list )
      logging.debug("{}.metadata([{}]) returned {}".format(__class__.__name__,','.join(lane_id_list),response))
      results = self.parse_response(response, required_keys = [self.config['metadata_key']])
      return results[self.config['metadata_key']]
   
   def in_silico_data(self, lane_id_list):
      endpoint = self.config['download_in_silico_data']
      logging.debug("{}.in_silico_data() using endpoint {}, passing list of {} sample IDs".format(__class__.__name__,endpoint,len(lane_id_list)))
      # this request will return a 404 of there are no in silico results for these samples
      # this is not an error, so a 404 must be caught, and an empty results set returned
      try:
         response = self.make_request( endpoint, post_data = lane_id_list )
      except urllib.error.HTTPError as e:
         if 404 == e.code:
            logging.debug("status {}: no in silico results currently available for these samples".format(e.code))
            return([])
         else:
            raise
      logging.debug("{}.in_silico_data([{}]) returned {}".format(__class__.__name__,','.join(lane_id_list),response))
      results = self.parse_response(response, required_keys = [self.config['in_silico_data_key']])
      return results[self.config['in_silico_data_key']]

   def make_request(self, endpoint, post_data=None):
      request_url       = self.config['base_url']+endpoint
      request_data      = None
      request_headers   = {}
      # if POST data were passed, convert to a UTF-8 JSON string
      if post_data is not None:
         assert ( isinstance(post_data, dict) or isinstance(post_data, list) ), "{}.make_request() requires post_data as a dict or a list, not {}".format(__class__.__name__,post_data)
         request_data = str(json.dumps(post_data))
         logging.debug("POST data for Monocle Download API: {}".format(request_data))
         request_data      = request_data.encode('utf-8')
         request_headers   = {'Content-type': 'application/json;charset=utf-8'}
      try:
         logging.info("request to Monocle Download: {}".format(request_url))
         http_request = urllib.request.Request(request_url, data = request_data, headers = request_headers)
         with urllib.request.urlopen( http_request ) as this_response:
            response_as_string = this_response.read().decode('utf-8')
            logging.debug("response from Monocle Download: {}".format(response_as_string))
      except urllib.error.HTTPError as e:
         if 404 == e.code:
            logging.info("HTTP response status {} (no data found) during Monocle Download request {}".format(e.code,request_url))
         else:
            logging.error("HTTP error during Monocle Download request {}".format(request_url))
         raise
      return response_as_string

   def parse_response(self, response_as_string, required_keys=[]):
      swagger_url  = self.config['base_url']+self.config['swagger'] # only because it may be useful for error messages
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
