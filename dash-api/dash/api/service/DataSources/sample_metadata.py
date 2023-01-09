import json
import logging
import urllib.parse
import urllib.request

import yaml

# logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='DEBUG')


class SampleMetadata:
    """provides access to pipeline status data"""

    def __init__(self, set_up=True):
        if set_up:
            self.set_up()

    def set_up(self):
        self.monocle_client = MonocleClient()

    def get_project_information(self, project):
        result = self.monocle_client.project_information(project)
        logging.debug("{}.get_project_information() result(s) = {}".format(__class__.__name__, result))

        return result

    def get_samples(self, project, exclude_lane_id=True, institution_keys=None):
        """
        Optionally pass a list of institution keys that filters samples according to submitting institution
        Optiomally pass exclude_lane_id=False to stop the lane ID being removed (the laner ID retrieved here
        is from the monocle db, where it was added for *some* samples for historical reasons, but it is not
        generally useful or necessarily accurate.  Lane IDs for a sample should be retrieved from MLWH)
        Returns a dict, keys are sample IDs, values are the selected metadata as a dict
        """
        results = self.monocle_client.samples(project)
        logging.info("{}.get_samples() got {} result(s)".format(__class__.__name__, len(results)))
        samples = []
        for this_result in results:
            if institution_keys is None or this_result["submitting_institution"] in institution_keys:
                # For historical reasons the following code was needed to replace the old keys
                # `sample_id` and `submitting_institution_id` with 'sanger_sample_id' and
                # 'submitting_institution', respectively.
                # TODO  see if we can now replace this, and simply return `results`, except with
                #       `lane_id` removed from each item in `results` (unless `exclude_lane_id`
                #       is False)
                this_sample = {
                    "sanger_sample_id": this_result["sanger_sample_id"],
                    "submitting_institution": this_result["submitting_institution"],
                    "public_name": this_result["public_name"],
                }
                if not exclude_lane_id:
                    this_sample["lane_id"] = this_result["lane_id"]
                logging.debug("result: {}".format(this_sample))
                samples.append(this_sample)
        return samples

    def get_samples_matching_metadata_filters(self, project, metadata_filters):
        """
        Pass a list of filters, as defined by the metadata API /sample_ids_matching_metadata endpoint.
        Returns a list of sample IDs matching the filter conditions
        """
        filters_payload = []
        for this_field in metadata_filters:
            these_values = metadata_filters[this_field]
            assert isinstance(
                these_values, list
            ), "{}.get_samples_matching_metadata_filters() expects metadata filter value to be a list, not {}".format(
                __class__.__name__, type(these_values)
            )
            filters_payload.append({"name": this_field, "values": these_values})
        logging.debug(
            "{}.get_samples_matching_metadata_filters() created filters payload {}".format(
                __class__.__name__, filters_payload
            )
        )

        results = self.monocle_client.filters(project, filters_payload)
        logging.info(
            "{}.get_samples_matching_metadata_filters() got {} results(s)".format(__class__.__name__, len(results))
        )
        return results

    def get_lanes_matching_in_silico_filters(self, project, in_silico_filters):
        """
        Pass a list of filters, as defined by the metadata API /lane_ids_matching_in_silico_data endpoint.
        Returns a list of lane IDs matching the filter conditions.
        (N.B. in silico data are identifier only by lane ID, not by sample ID)
        """
        filters_payload = []
        for this_field in in_silico_filters:
            these_values = in_silico_filters[this_field]
            assert isinstance(
                these_values, list
            ), "{}.get_lanes_matching_in_silico_filters() expects in silico filter value to be a list, not {}".format(
                __class__.__name__, type(these_values)
            )
            filters_payload.append({"name": this_field, "values": these_values})
        logging.debug(
            "{}.get_lanes_matching_in_silico_filters() created filters payload {}".format(
                __class__.__name__, filters_payload
            )
        )

        results = self.monocle_client.filters_in_silico(project, filters_payload)
        logging.info(
            "{}.get_lanes_matching_in_silico_filters() got {} results(s)".format(__class__.__name__, len(results))
        )
        return results

    def get_lanes_matching_qc_data_filters(self, project, qc_data_filters):
        """
        Pass a list of filters, as defined by the metadata API /lane_ids_matching_qc_data endpoint.
        Returns a list of lane IDs matching the filter conditions.
        (N.B. in silico data are identifier only by lane ID, not by sample ID)
        """
        filters_payload = []
        for this_field in qc_data_filters:
            these_values = qc_data_filters[this_field]
            assert isinstance(
                these_values, list
            ), "{}.get_lanes_matching_qc_data_filters() expects QC data filter value to be a list, not {}".format(
                __class__.__name__, type(these_values)
            )
            filters_payload.append({"name": this_field, "values": these_values})
        logging.debug(
            "{}.get_lanes_matching_qc_data_filters() created filters payload {}".format(
                __class__.__name__, filters_payload
            )
        )

        results = self.monocle_client.filters_qc_data(project, filters_payload)

        logging.info(
            "{}.get_lanes_matching_qc_data_filters() got {} results(s)".format(__class__.__name__, len(results))
        )
        return results


class ProtocolError(Exception):
    pass


class MonocleClient:
    data_sources_config = "data_sources.yml"
    metadata_common_source = "metadata_api_common"
    metadata_project_source = {"juno": "metadata_api_juno", "gps": "metadata_api_gps"}
    required_config_params = [
        "base_url",
        "project_information",
        "project_information_key",
        "samples",
        "filter_by_metadata",
        "filter_by_in_silico",
        "samples_key",
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

    def project_information(self, project):
        if project not in self.config:
            logging.error(
                "data source config file {} does not provide the required parameter {}".format(
                    self.data_sources_config,
                    project,
                )
            )
            raise KeyError("{} could not be found in data source config dict".format(project))

        this_config = self.config[project]
        for param in ["base_url", "project_information", "project_information_key"]:
            if param not in this_config:
                raise KeyError("{} could not be found in data source config project dict".format(param))

        endpoint_url = this_config["base_url"] + this_config["project_information"]
        logging.debug("{}.project_information() using endpoint {}".format(__class__.__name__, endpoint_url))
        response = self.make_request(endpoint_url)
        logging.debug("{}.project_information() returned {}".format(__class__.__name__, response))
        project_information_key = this_config["project_information_key"]
        result = self.parse_response(endpoint_url, response, required_keys=[project_information_key])
        return result[project_information_key]

    def samples(self, project):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["samples"]
        logging.debug("{}.samples() using endpoint {}".format(__class__.__name__, endpoint_url))
        response = self.make_request(endpoint_url)
        logging.debug("{}.samples() returned {}".format(__class__.__name__, response))
        results = self.parse_response(endpoint_url, response, required_keys=[this_config["samples_key"]])
        return results[this_config["samples_key"]]

    def filters(self, project, filters):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["filter_by_metadata"]
        logging.debug("{}.filters() using endpoint {}, query = {}".format(__class__.__name__, endpoint_url, filters))
        response = self.make_request(endpoint_url, post_data=filters)
        logging.debug("{}.filters() returned {}".format(__class__.__name__, response))
        results = json.loads(response)
        return results

    def filters_in_silico(self, project, filters):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["filter_by_in_silico"]
        logging.debug("{}.filters() using endpoint {}, query = {}".format(__class__.__name__, endpoint_url, filters))
        response = self.make_request(endpoint_url, post_data=filters)
        logging.debug("{}.filters() returned {}".format(__class__.__name__, response))
        results = json.loads(response)
        return results

    def filters_qc_data(self, project, filters):
        this_config = self.config[project]
        endpoint_url = this_config["base_url"] + this_config["filter_by_qc_data"]
        logging.debug("{}.filters() using endpoint {}, query = {}".format(__class__.__name__, endpoint_url, filters))
        response = self.make_request(endpoint_url, post_data=filters)
        logging.debug("{}.filters() returned {}".format(__class__.__name__, response))
        results = json.loads(response)
        return results

    def make_request(self, request_url, post_data=None):
        request_data = None
        request_headers = {}
        # if POST data were passed, convert to a UTF-8 JSON string
        if post_data is not None:
            assert isinstance(post_data, dict) or isinstance(
                post_data, list
            ), "{}.make_request() requires post_data as a dict or a list, not {}".format(__class__.__name__, post_data)
            request_data = str(json.dumps(post_data))
            logging.debug("POST data for Metadata API: {}".format(request_data))
            request_data = request_data.encode("utf-8")
            request_headers = {"Content-type": "application/json;charset=utf-8"}
        try:
            logging.info("request to Metadata API: {}".format(request_url))
            logging.debug(
                "\nRequest to metadata API:\nURL = {}\nheaders = {}\nPOST data = {}".format(
                    request_url, request_headers, request_data
                )
            )
            http_request = urllib.request.Request(request_url, data=request_data, headers=request_headers)
            with urllib.request.urlopen(http_request) as this_response:
                response_as_string = this_response.read().decode("utf-8")
                logging.debug("response from Metadata API: {}".format(response_as_string))
        except urllib.error.HTTPError as e:
            msg = "HTTP error during Metadata API request {}: {} {}\nData:\n{}".format(
                request_url, e.code, e.read().decode("utf-8"), request_data
            )
            if "404" in str(e):
                logging.info(msg)
            else:
                logging.error(msg)
            raise e
        return response_as_string

    def parse_response(self, endpoint, response_as_string, required_keys=[]):
        results_data = json.loads(response_as_string)
        if not isinstance(results_data, dict):
            error_message = "request to '{}' did not return a dict as expected".format(endpoint)
            raise ProtocolError(error_message)
        for required_key in required_keys:
            try:
                results_data[required_key]
            except KeyError:
                error_message = "response data did not contain the expected key '{}'".format(required_key)
                raise ProtocolError(error_message)
        return results_data
