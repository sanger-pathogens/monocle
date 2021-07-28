import http.client
import json
import logging
import urllib.parse
import urllib.request
import yaml


# class DataSourceParamError(Exception):
#    """ exception when data source methods are called with invalid parameter(s) """
#    pass

class SampleMetadata:
    """ provides access to pipeline status data """

    def __init__(self, set_up=True):
        if set_up:
            self.set_up()

    def set_up(self):
        self.monocle_client = Monocle_Client()

    def get_institution_names(self):
        result = self.monocle_client.institutions()
        logging.debug("{}.get_institution_names() result(s) = {}".format(__class__.__name__, result))

        return result

    def get_samples(self, exclude_lane_id=True, institutions=None):
        """
        Pass a list of institutions.
        Returns a dict, keys are sample IDs, values are the sequencing status data as a dict
        If a sample ID is passed that is not found by the API, it will be missing from the returned dict.
        """
        results_list = self.monocle_client.samples()
        logging.info("{}.get_samples() got {} result(s)".format(__class__.__name__, len(results_list)))
        # turn results list into dict keys on the sample IDs
        results_by_sample_id = []
        for this_result in results_list:
            this_result.pop('id')
            results_by_sample_id.append(this_result)
        if institutions:
            for result in results_by_sample_id:
                if result['submitting_institution'] not in institutions:
                    results_by_sample_id.pop(result)
        if exclude_lane_id:
            for result in results_by_sample_id:
                result.pop('lane_id', None)
        return results_by_sample_id


class ProtocolError(Exception):
    pass


class Monocle_Client:
    data_sources_config = 'data_sources.yml'
    data_source = 'monocle_metadata_api'
    required_config_params = ['base_url',
                              'swagger',
                              'institutions',
                              'samples',
                              ]

    def __init__(self, set_up=True):
        if set_up:
            self.set_up(self.data_sources_config)

    def set_up(self, config_file_name):
        with open(config_file_name, 'r') as file:
            data_sources = yaml.load(file, Loader=yaml.FullLoader)
            self.config = data_sources[self.data_source]
        for required_param in self.required_config_params:
            if not required_param in self.config:
                logging.error("data source config file {} does not provide the required paramter {}.{}".format(
                    self.data_sources_config, self.data_source, required_param))
                raise KeyError

    def institutions(self):
        endpoint = self.config['institutions']
        logging.debug("{}.institutions() using endpoint {}".format(__class__.__name__, endpoint))
        response = self.make_request(endpoint)
        logging.debug("{}.institutions() returned {}".format(__class__.__name__, response))
        results = self.parse_response(response)
        return results[self.config['institutions']]

    def samples(self):
        endpoint = self.config['samples']
        logging.debug(
            "{}.samples() using endpoint {}".format(__class__.__name__, endpoint))
        response = self.make_request(endpoint)
        logging.debug("{}.samples() returned {}".format(__class__.__name__, response))
        results = self.parse_response(response)
        return results[self.config['samples']]

    def make_request(self, endpoint, post_data=None):
        request_url = self.config['base_url'] + endpoint
        request_data = None
        request_headers = {}
        # if POST data were passed, convert to a UTF-8 JSON string
        if post_data is not None:
            assert (isinstance(post_data, dict) or isinstance(post_data,
                                                              list)), "{}.make_request() requires post_data as a dict or a list, not {}".format(
                __class__.__name__, post_data)
            request_data = str(json.dumps(post_data))
            logging.debug("POST data for Metadata API: {}".format(request_data))
            request_data = request_data.encode('utf-8')
            request_headers = {'Content-type': 'application/json;charset=utf-8'}
        try:
            logging.info("request to Metadata API: {}".format(request_url))
            http_request = urllib.request.Request(request_url, data=request_data, headers=request_headers)
            with urllib.request.urlopen(http_request) as this_response:
                response_as_string = this_response.read().decode('utf-8')
                logging.debug("response from Metadata API: {}".format(response_as_string))
        except urllib.error.HTTPError:
            logging.error("HTTP error during Metadata API request {}".format(request_url))
            raise
        return response_as_string

    def parse_response(self, response_as_string, required_keys=[]):
        swagger_url = self.config['base_url'] + self.config[
            'swagger']  # only because it may be useful for error messages
        results_data = json.loads(response_as_string)
        if not isinstance(results_data, dict):
            error_message = "request to '{}' did not return a dict as expected (see API documentation at {})".format(
                endpoint, swagger_url)
            raise ProtocolError(error_message)
        for required_key in required_keys:
            try:
                results_data[required_key]
            except KeyError:
                error_message = "response data did not contain the expected key '{}' (see API documentation at {})".format(
                    required_key, swagger_url)
                raise ProtocolError(error_message)
        return results_data
