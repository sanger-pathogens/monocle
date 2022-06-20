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
            if institution_keys is None or this_result["submitting_institution_key"] in institution_keys:
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
                    "host_status": this_result["host_status"],
                    "serotype": this_result["serotype"],
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
            ), "{}.get_lanes_matching_in_silico_filters() expects metadata filter value to be a list, not {}".format(
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

    def get_distinct_values(self, project, fields, institution_keys):
        """
        Pass a dict with one or more of 'metadata', 'in silico' or 'qc data'
        as keys; values are arrays of field names.
        Returns array of GetDistinctValuesOutput objects (as defined in OpenAPI spec.)
        """
        results = []
        for this_field_type in fields:
            field_list = fields[this_field_type]
            if "metadata" == this_field_type:
                this_field_list = self.monocle_client.distinct_values(project, field_list, institution_keys)
            elif "in silico" == this_field_type:
                this_field_list = self.monocle_client.distinct_in_silico_values(project, field_list, institution_keys)
            elif "qc data" == this_field_type:
                this_field_list = self.monocle_client.distinct_qc_data_values(project, field_list, institution_keys)
            else:
                logging.error(
                    "{}.get_distinct_values() was passed field type {}: should be one of 'metadata', 'in silico' or 'qc data' ".format(
                        __class__.__name__, this_field_type
                    )
                )
                raise ValueError("{} is not a recognised field type".format(this_field_type))
            results.append({"field type": this_field_type, "fields": this_field_list})

        logging.debug("{}.get_distinct_values() got {}".format(__class__.__name__, results))
        return results


class ProtocolError(Exception):
    pass


class MonocleClient:
    data_sources_config = "data_sources.yml"
    data_source = "monocle_metadata_api"
    required_config_params = [
        "base_url",
        "swagger",
        "samples",
        "filter_by_metadata",
        "filter_by_in_silico",
        "samples_key",
        "distinct_values",
        "distinct_in_silico_values",
        "distinct_qc_data_values",
        "distinct_values_key",
    ]

    def __init__(self, set_up=True):
        if set_up:
            self.set_up(self.data_sources_config)

    def set_up(self, config_file_name):
        with open(config_file_name, "r") as file:
            data_sources = yaml.load(file, Loader=yaml.FullLoader)
        self.config = data_sources[self.data_source]
        for required_param in self.required_config_params:
            if required_param not in self.config:
                logging.error(
                    "data source config file {} does not provide the required paramter {}.{}".format(
                        self.data_sources_config, self.data_source, required_param
                    )
                )
                raise KeyError

    def samples(self, project):
        endpoint = self.config["samples"]
        logging.debug("{}.samples() using endpoint {}".format(__class__.__name__, endpoint))
        logging.warning(
            '{}.samples was passed project "{}" but the metadata API does not support this yet'.format(
                __class__.__name__, project
            )
        )
        # TODO pass `project` when it is implemented on the endpoint
        response = self.make_request(endpoint)
        logging.debug("{}.samples() returned {}".format(__class__.__name__, response))
        results = self.parse_response(endpoint, response, required_keys=[self.config["samples_key"]])
        return results[self.config["samples_key"]]

    def filters(self, project, filters):
        endpoint = self.config["filter_by_metadata"]
        logging.debug("{}.filters() using endpoint {}, query = {}".format(__class__.__name__, endpoint, filters))
        logging.warning(
            '{}.filters was passed project "{}" but the metadata API does not support this yet'.format(
                __class__.__name__, project
            )
        )
        # TODO pass `project` when it is implemented on the endpoint
        response = self.make_request(endpoint, post_data=filters)
        logging.debug("{}.filters() returned {}".format(__class__.__name__, response))
        results = json.loads(response)
        return results

    def filters_in_silico(self, project, filters):
        endpoint = self.config["filter_by_in_silico"]
        logging.debug("{}.filters() using endpoint {}, query = {}".format(__class__.__name__, endpoint, filters))
        logging.warning(
            '{}.filters_in_silico was passed project "{}" but the metadata API does not support this yet'.format(
                __class__.__name__, project
            )
        )
        # TODO pass `project` when it is implemented on the endpoint
        response = self.make_request(endpoint, post_data=filters)
        logging.debug("{}.filters() returned {}".format(__class__.__name__, response))
        results = json.loads(response)
        return results

    def distinct_values(self, project, fields, institution_keys):
        endpoint = self.config["distinct_values"]
        return self._distinct_values_common(endpoint, project, fields, institution_keys)

    def distinct_in_silico_values(self, project, fields, institution_keys):
        endpoint = self.config["distinct_in_silico_values"]
        return self._distinct_values_common(endpoint, project, fields, institution_keys)

    def distinct_qc_data_values(self, project, fields, institution_keys):
        endpoint = self.config["distinct_qc_data_values"]
        return self._distinct_values_common(endpoint, project, fields, institution_keys)

    def _distinct_values_common(self, endpoint, project, fields, institution_keys):
        query = {"fields": fields, "institutions": institution_keys}
        logging.debug("{}.distinct_values() using endpoint {}, query: {}".format(__class__.__name__, endpoint, query))
        logging.warning(
            '{}._distinct_values_common was passed project "{}" but the metadata API does not support this yet'.format(
                __class__.__name__, project
            )
        )
        # TODO pass `project` when it is implemented on the endpoint
        response = self.make_request(endpoint, post_data=query)
        logging.debug("{}.distinct_values() returned {}".format(__class__.__name__, response))
        results = json.loads(response)
        return results[self.config["distinct_values_key"]]

    def make_request(self, endpoint, post_data=None):
        request_url = self.config["base_url"] + endpoint
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
        swagger_url = (
            self.config["base_url"] + self.config["swagger"]
        )  # only because it may be useful for error messages
        results_data = json.loads(response_as_string)
        if not isinstance(results_data, dict):
            error_message = "request to '{}' did not return a dict as expected (see API documentation at {})".format(
                endpoint, swagger_url
            )
            raise ProtocolError(error_message)
        for required_key in required_keys:
            try:
                results_data[required_key]
            except KeyError:
                error_message = (
                    "response data did not contain the expected key '{}' (see API documentation at {})".format(
                        required_key, swagger_url
                    )
                )
                raise ProtocolError(error_message)
        return results_data
