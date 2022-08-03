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
    """provides access to monocle metadata"""

    def __init__(self, set_up=True):
        if set_up:
            self.set_up()

    def set_up(self):
        self.download_client = MonocleDownloadClient()

    def get_metadata(self, project, lane_id_list):
        logging.debug("{}.get_metadata() called with {}".format(__class__.__name__, lane_id_list))
        results_list = self.download_client.metadata(project, lane_id_list)
        assert isinstance(
            results_list, list
        ), "MonocleDownloadClient.metadata() was expected to return a list, not {}".format(type(results_list))
        logging.debug("{}.get_metadata() result 1: {}".format(__class__.__name__, results_list[0]))
        logging.info("{}.get_metadata() got {} result(s)".format(__class__.__name__, len(results_list)))
        return results_list

    def get_in_silico_data(self, project, lane_id_list):
        logging.debug("{}.get_in_silico_data() called with {}".format(__class__.__name__, lane_id_list))
        results_list = self.download_client.in_silico_data(project, lane_id_list)
        assert isinstance(
            results_list, list
        ), "MonocleDownloadClient.in_silico_data() was expected to return a list, not {}".format(type(results_list))
        if len(results_list) > 0:
            logging.debug("{}.get_in_silico_data() result 1: {}".format(__class__.__name__, results_list[0]))
        logging.info("{}.get_in_silico_data() got {} result(s)".format(__class__.__name__, len(results_list)))
        return results_list

    def get_qc_data(self, project, lane_id_list):
        logging.debug("{}.get_qc_data() called with {}".format(__class__.__name__, lane_id_list))
        results_list = self.download_client.qc_data(project, lane_id_list)
        assert isinstance(
            results_list, list
        ), "MonocleDownloadClient.qc_data() was expected to return a list, not {}".format(type(results_list))
        if len(results_list) > 0:
            logging.debug("{}.get_qc_data() result 1: {}".format(__class__.__name__, results_list[0]))
        logging.info("{}.get_iqc_data() got {} result(s)".format(__class__.__name__, len(results_list)))
        return results_list


class ProtocolError(Exception):
    pass


class MonocleDownloadClient:

    data_sources_config = "data_sources.yml"
    metadata_common_source = "metadata_api_common"
    metadata_project_source = {"juno": "metadata_api_juno", "gps": "metadata_api_gps"}
    required_config_params = [
        "base_url",
        "download",
        "metadata_key",
        "download_in_silico_data",
        "in_silico_data_key",
        "download_qc_data",
        "qc_data_key",
    ]

    def __init__(self, set_up=True):
        if set_up:
            self.set_up(self.data_sources_config)

    def set_up(self, config_file_name):
        self.config = {}
        with open(config_file_name, "r") as file:
            data_sources = yaml.load(file, Loader=yaml.FullLoader)
            common_config = data_sources[self.metadata_common_source]
            for this_project in self.metadata_project_source:
                self.config[this_project] = {
                    **common_config,
                    **data_sources[self.metadata_project_source[this_project]],
                }
        for this_project in self.config:
            for required_param in self.required_config_params:
                if required_param not in self.config[this_project]:
                    logging.error(
                        "data source config file {} does not provide the required parameter {} (should be in section {} or {})".format(
                            self.data_sources_config,
                            required_param,
                            self.metadata_common_source,
                            self.metadata_project_source[this_project],
                        )
                    )
                    raise KeyError("{} could not be found in data source config dict".format(required_param))

    def metadata(self, project, lane_id_list):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["download"]
        logging.debug(
            "{}.metadata() using endpoint {}, passing list of {} sample IDs".format(
                __class__.__name__, endpoint_url, len(lane_id_list)
            )
        )
        response = self.make_request(endpoint_url, post_data=lane_id_list)
        logging.debug("{}.metadata([{}]) returned {}".format(__class__.__name__, ",".join(lane_id_list), response))
        results = self.parse_response(endpoint_url, response, required_keys=[this_config["metadata_key"]])
        return results[this_config["metadata_key"]]

    def in_silico_data(self, project, lane_id_list):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["download_in_silico_data"]
        logging.debug(
            "{}.in_silico_data() using endpoint {}, passing list of {} sample IDs".format(
                __class__.__name__, endpoint_url, len(lane_id_list)
            )
        )
        # this request will return a 404 if there are no in silico results for these samples
        # this is not an error, so a 404 must be caught, and an empty results set returned
        try:
            response = self.make_request(endpoint_url, post_data=lane_id_list)
        except urllib.error.HTTPError as e:
            if 404 == e.code:
                logging.debug("status {}: no in silico results currently available for these samples".format(e.code))
                return []
            else:
                raise
        logging.debug(
            "{}.in_silico_data([{}]) returned {}".format(__class__.__name__, ",".join(lane_id_list), response)
        )
        results = self.parse_response(endpoint_url, response, required_keys=[this_config["in_silico_data_key"]])
        return results[this_config["in_silico_data_key"]]

    def qc_data(self, project, lane_id_list):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["download_qc_data"]
        logging.debug(
            "{}.qc_data() using endpoint {}, passing list of {} sample IDs".format(
                __class__.__name__, endpoint_url, len(lane_id_list)
            )
        )
        # this request will return a 404 if there are no QC data results for these samples
        # this is not an error, so a 404 must be caught, and an empty results set returned
        try:
            response = self.make_request(endpoint_url, post_data=lane_id_list)
        except urllib.error.HTTPError as e:
            if 404 == e.code:
                logging.debug("status {}: no QC data results currently available for these samples".format(e.code))
                return []
            else:
                raise
        logging.debug("{}.qc_data([{}]) returned {}".format(__class__.__name__, ",".join(lane_id_list), response))
        results = self.parse_response(endpoint_url, response, required_keys=[this_config["qc_data_key"]])
        return results[this_config["qc_data_key"]]

    def make_request(self, request_url, post_data=None):
        request_data = None
        request_headers = {}
        # if POST data were passed, convert to a UTF-8 JSON string
        if post_data is not None:
            assert isinstance(post_data, dict) or isinstance(
                post_data, list
            ), "{}.make_request() requires post_data as a dict or a list, not {}".format(__class__.__name__, post_data)
            request_data = str(json.dumps(post_data))
            logging.debug("POST data for Monocle Download API: {}".format(request_data))
            request_data = request_data.encode("utf-8")
            request_headers = {"Content-type": "application/json;charset=utf-8"}
        try:
            logging.info("request to Monocle Download: {}".format(request_url))
            http_request = urllib.request.Request(request_url, data=request_data, headers=request_headers)
            with urllib.request.urlopen(http_request) as this_response:
                response_as_string = this_response.read().decode("utf-8")
                logging.debug("response from Monocle Download: {}".format(response_as_string))
        except urllib.error.HTTPError as e:
            if 404 == e.code:
                logging.info(
                    "HTTP response status {} (no data found) during Monocle Download request {}".format(
                        e.code, request_url
                    )
                )
            else:
                logging.error(
                    "HTTP status {} during Monocle Download request {}\n{}".format(
                        e.code, request_url, e.read().decode("utf-8")
                    )
                )
            raise
        return response_as_string

    def parse_response(self, endpoint_url, response_as_string, required_keys=[]):
        results_data = json.loads(response_as_string)
        if not isinstance(results_data, dict):
            error_message = "request to '{}' did not return a dict as expected".format(endpoint_url)
            raise ProtocolError(error_message)
        for required_key in required_keys:
            try:
                results_data[required_key]
            except KeyError:
                error_message = "response data did not contain the expected key '{}'".format(required_key)
                raise ProtocolError(error_message)
        return results_data
