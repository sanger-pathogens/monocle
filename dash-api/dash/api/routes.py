import errno
import json
import logging
import os
from http import HTTPStatus
from http.client import HTTPS_PORT
from itertools import islice
from math import ceil
from pathlib import Path
from time import sleep, time
from urllib.error import HTTPError
from uuid import uuid4

import yaml
from dash.api.exceptions import NotAuthorisedException
from dash.api.service.service_factory import ServiceFactory
from dash.api.utils.file import ZIP_SUFFIX, complete_zipfile, zip_files
from flask import Response, jsonify, request

logger = logging.getLogger()

# Testing only
ServiceFactory.TEST_MODE = False

DATA_INST_VIEW_ENVIRON = {"juno": "JUNO_DATA_INSTITUTION_VIEW", "gps": "GPS_DATA_INSTITUTION_VIEW"}

OPENAPI_SPEC_FILE = "./dash/interface/openapi.yml"
GET_METADATA_INPUT_SCHEMA = "GetMetadataInput"

AUTH_COOKIE_NAME_ENVIRON = "AUTH_COOKIE_NAME"


def set_auth_cookie_route(body):
    """Given a username and password provided by the user, set cookie to be used by NGINX auth module
    Response is a redirect to URL in the X-Target request header ('/' by default)
    """
    try:
        username_provided = body["username"]
        password_provided = body["password"]
    except KeyError:
        logging.error("endpoint handler {} must be passed the username and password provided".format(__name__))
        raise

    auth_token = ServiceFactory.authentication_service().get_auth_token(username_provided, password_provided)
    target_url = call_request_headers().get("X-Target", "/")

    auth_response = Response(
        "Redirect to {}".format(target_url),
        content_type="application/json; charset=UTF-8",
        status=HTTPStatus.TEMPORARY_REDIRECT,
        headers={"Location": target_url},
    )

    cookie_name = os.environ[AUTH_COOKIE_NAME_ENVIRON]
    auth_response.set_cookie(
        cookie_name, value=auth_token.encode("utf8"), max_age=None  # age in seconds; `None` for session cookie
    )

    return auth_response


def delete_auth_cookie_route():
    """Delete the cookie to be used by NGINX auth module
    Response is a redirect to URL in the X-Target request header ('/' by default)
    """
    target_url = call_request_headers().get("X-Target", "/")

    delete_cookie_response = Response(
        "Redirect to {}".format(target_url),
        content_type="application/json; charset=UTF-8",
        status=HTTPStatus.TEMPORARY_REDIRECT,
        headers={"Location": target_url},
    )

    cookie_name = os.environ[AUTH_COOKIE_NAME_ENVIRON]
    delete_cookie_response.set_cookie(cookie_name, value="", expires=0)  # expires immediately

    return delete_cookie_response


def get_user_details_route():
    """Given a username retrieve all details for that user"""
    data = ServiceFactory.user_service(get_authenticated_username()).user_details
    response_dict = {"user_details": data}
    return call_jsonify(response_dict), HTTPStatus.OK


def get_batches_route():
    """Get dashboard batch information"""
    data = ServiceFactory.sample_tracking_service(get_authenticated_username()).get_batches()
    response_dict = {"batches": data}
    return call_jsonify(response_dict), HTTPStatus.OK


def get_institutions_route():
    """Get a list of institutions"""
    data = ServiceFactory.sample_tracking_service(get_authenticated_username()).get_institutions()
    response_dict = {"institutions": data}
    return call_jsonify(response_dict), HTTPStatus.OK


def get_progress_route():
    """Get dashboard progress graph information"""
    data = ServiceFactory.sample_tracking_service(get_authenticated_username()).get_progress()
    response_dict = {"progress_graph": {"data": data}}
    return call_jsonify(response_dict), HTTPStatus.OK


def sequencing_status_summary_route():
    """Get dashboard sequencing status summary information"""
    data = ServiceFactory.sample_tracking_service(get_authenticated_username()).sequencing_status_summary()
    response_dict = {"sequencing_status": data}
    return call_jsonify(response_dict), HTTPStatus.OK


def project_route():
    """Get project information"""
    project_data = ServiceFactory.sample_tracking_service(get_authenticated_username()).project_information()
    response_dict = {"project": project_data}
    return call_jsonify(response_dict), HTTPStatus.OK


def pipeline_status_summary_route():
    """Get dashboard pipeline status summary information"""
    data = ServiceFactory.sample_tracking_service(get_authenticated_username()).pipeline_status_summary()
    response_dict = {"pipeline_status": data}
    return call_jsonify(response_dict), HTTPStatus.OK


def get_field_attributes_route():
    data = ServiceFactory.sample_data_service(get_authenticated_username()).get_field_attributes()
    response_dict = {"field_attributes": data}
    return call_jsonify(response_dict), HTTPStatus.OK


def get_metadata_route(body):
    """Get sample metadata based on standard sample filter"""
    logging.info("endpoint handler {} was passed body = {}".format(__name__, body))
    sample_filters = body["sample filters"]
    defaults = get_metadata_input_default()
    return_as_csv = body.get("as csv", defaults["as csv"])
    csv_filename = body.get("csv filename", defaults["csv filename"])
    metadata_columns = body.get("metadata columns", defaults["metadata columns"])
    in_silico_columns = body.get("in silico columns", defaults["in silico columns"])
    qc_data_columns = body.get("qc data columns", defaults["qc data columns"])

    try:
        if return_as_csv:
            # note the metadata CSV here does not include data download URLs
            # this is because the sample filters could match samples from multiple institutions, and download
            # links for multiple institutions are not currently supported with CSV metadata downloads
            return _metadata_as_csv_response(
                ServiceFactory.sample_data_service(get_authenticated_username()).get_csv_download(
                    csv_filename, sample_filters
                )
            )
        else:
            # setting column filter params to '_ALL' means all columns should be returned
            if "_ALL" == metadata_columns[0]:
                metadata_columns = None
            if "_ALL" == in_silico_columns[0]:
                in_silico_columns = None
            if "_ALL" == qc_data_columns[0]:
                qc_data_columns = None
            metadata = ServiceFactory.sample_data_service(get_authenticated_username()).get_metadata(
                sample_filters,
                start_row=body.get("start row", None),
                num_rows=body.get("num rows", defaults["num rows"]),
                include_in_silico=body.get("in silico", defaults["in silico"]),
                include_qc_data=body.get("qc data", defaults["qc data"]),
                metadata_columns=metadata_columns,
                in_silico_columns=in_silico_columns,
                qc_data_columns=qc_data_columns,
            )
            if metadata is None:
                return Response(
                    "No matching samples were found",
                    content_type="text/plain; charset=UTF-8",
                    status=HTTPStatus.NOT_FOUND,
                )
            return call_jsonify(metadata), HTTPStatus.OK
    except HTTPError as e:
        if "400" in str(e):
            return "Bad request", HTTPStatus.BAD_REQUEST
        raise e


def get_distinct_values_route(body):
    """Return distinct values found in metadata, in silico or QC data fields"""
    logging.info("endpoint handler {} was passed body = {}".format(__name__, body))
    monocle_data = ServiceFactory.sample_data_service(get_authenticated_username())
    field_types = ["metadata", "in silico", "qc data"]

    fields_list = body["fields"]
    sample_filters = body.get("sample filters", None)

    # validate *types* of field named in request
    fields_types_found = []
    distinct_values_request = {}
    for this_obj in fields_list:
        this_field_type = this_obj["field type"]
        if this_field_type in fields_types_found:
            logging.info(
                "{}.get_distinct_values_route() was passed field type {} more than once".format(
                    __name__, this_field_type
                )
            )
            return (
                "Field type {} was included in the request more than once".format(this_field_type),
                HTTPStatus.BAD_REQUEST,
            )
        if this_field_type not in field_types:
            logging.info(
                "{}.get_distinct_values_route() was passed field type {}: should be one of {}".format(
                    __name__, this_field_type, field_types
                )
            )
            return (
                "Invalid field type {}: should be one of {}".format(this_field_type, field_types),
                HTTPStatus.BAD_REQUEST,
            )
        fields_types_found.append(this_field_type)
        distinct_values_request[this_field_type] = this_obj["field names"]

    distinct_values = monocle_data.get_distinct_values(distinct_values_request, sample_filters=sample_filters)

    if distinct_values is None:
        # this means a non-existent field was asked for => customized 404
        return "One or more of the requested fields could not be found", HTTPStatus.NOT_FOUND

    response_dict = {"distinct values": distinct_values}
    return call_jsonify(response_dict), HTTPStatus.OK


def bulk_download_info_route(body):
    """Get download estimate in reponse to the user's changing parameters on the bulk download page"""
    logging.info("endpoint handler {} was passed body = {}".format(__name__, body))
    sample_filters, assemblies, annotations, reads = _parse_BulkDownloadInput(body)

    try:
        download_info = ServiceFactory.sample_data_service(get_authenticated_username()).get_bulk_download_info(
            sample_filters, assemblies=assemblies, annotations=annotations, reads=reads
        )
    except HTTPError as e:
        if "400" in str(e):
            return "Bad request", HTTPStatus.BAD_REQUEST
        raise e
    if download_info is None:
        return Response(
            "No matching samples were found", content_type="text/plain; charset=UTF-8", status=HTTPStatus.NOT_FOUND
        )
    return call_jsonify(download_info), HTTPStatus.OK


def bulk_download_urls_route(body):
    """Get download links to ZIP files w/ lanes corresponding to the request parameters"""
    logging.info("endpoint handler {} was passed body = {}".format(__name__, body))
    sample_filters, assemblies, annotations, reads = _parse_BulkDownloadInput(body)
    try:
        monocle_data = ServiceFactory.sample_data_service(get_authenticated_username())
        samples = monocle_data.get_filtered_samples(sample_filters)
    # catch 404 and 400s from metadata API
    except HTTPError as e:
        if "404" in str(e):
            return Response(
                "No matching samples were found", content_type="text/plain; charset=UTF-8", status=HTTPStatus.NOT_FOUND
            )
        elif "400" in str(e):
            return "Bad request", HTTPStatus.BAD_REQUEST
        raise e

    public_name_to_lane_files = monocle_data.get_public_name_to_lane_files_dict(
        samples, assemblies=assemblies, annotations=annotations, reads=reads
    )
    logging.debug("Public name to data files: {}".format(public_name_to_lane_files))

    download_param_file_location = monocle_data.get_bulk_download_location()
    if not Path(download_param_file_location).is_dir():
        logging.error("data downloads directory {} does not exist".format(download_param_file_location))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), download_param_file_location)

    # the data we want to serialize contains PosixPath objects that we need to make into strings
    data_inst_view_environ = DATA_INST_VIEW_ENVIRON[get_authenticated_project()]
    data_inst_view_path = os.environ[data_inst_view_environ]
    for this_public_name in public_name_to_lane_files:
        file_paths_as_strings = []
        for this_file in public_name_to_lane_files[this_public_name]:
            # this slice removes the leading path defined by the environment variable `data_inst_view_environ`
            # to (a) avoid exposing our file system structure oin plublically accessible file, and
            # (b) ensure downlaods don't break if we move the data to a new directory
            file_paths_as_strings.append(str(this_file)[len(data_inst_view_path) :])
        public_name_to_lane_files[this_public_name] = file_paths_as_strings

    # limit the number of samples to be included in each ZIP archive
    max_samples_per_zip = body.get("max samples per zip", None)
    if max_samples_per_zip is None:
        # if not passed, get value from config file
        max_samples_per_zip = monocle_data.get_bulk_download_max_samples_per_zip(including_reads=reads)

    download_url_list = []
    start = 0
    total = len(public_name_to_lane_files)
    num_downloads = ceil(total / max_samples_per_zip)
    logging.debug(
        "total = {}, max_samples_per_zip = {}, num_downloads = {}".format(total, max_samples_per_zip, num_downloads)
    )
    samples_in_each = ceil(total / num_downloads)
    while total > start:
        this_zip_archive_contents = dict(islice(public_name_to_lane_files.items(), start, (start + samples_in_each), 1))
        download_token = uuid4().hex
        download_param_file_name = "{}.params.json".format(download_token)
        file_written = write_text_file(
            os.path.join(download_param_file_location, download_param_file_name), json.dumps(this_zip_archive_contents)
        )
        logging.debug(
            "wrote download params for samples {} to {} to {}".format(
                (start + 1), (start + samples_in_each), file_written
            )
        )
        download_url_list.append("/".join([monocle_data.get_bulk_download_route(), download_token]))
        start += samples_in_each

    return call_jsonify({"download_urls": download_url_list}), HTTPStatus.OK


def data_download_route(token: str):
    """Provides download if the ZIP archive providing the data associated with the token passed.
    The token identifies a JSON file that holds the parameter required to create the ZIP archive.
    Unless the ZIP archive exists (i.e. this download has been requsetd before) the ZIP archive is
    created.
    By default 303 response is returned providing a download of the ZIP archive via the static file route;
    but if the query uses `?redirect=false` then the resp[onse is a 200 with the static download
    route in the response body.
    If the JSON file isn't found a 404 is returned (this will happen if the download link that
    was used is old, and the housekeeping cron job has deleted the JSON file in the interim).
    """
    redirect_wanted = "true" == call_request_args().get("redirect", "true").lower()
    logging.info(
        "endpoint handler {} was passed token = {} , redirect flag({}) = {}".format(
            __name__, token, type(redirect_wanted), redirect_wanted
        )
    )
    monocle_data = ServiceFactory.sample_data_service(get_authenticated_username())

    logging.info("Data download request headers:\n{}".format(call_request_headers()))

    download_param_file_location = monocle_data.get_bulk_download_location()
    if not Path(download_param_file_location).is_dir():
        logging.error("data downloads directory {} does not exist".format(download_param_file_location))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), download_param_file_location)

    zip_file_basename = token
    zip_file_name = zip_file_basename + ZIP_SUFFIX
    if Path(download_param_file_location, zip_file_name).is_file():
        # The ZIP file exists. This means we have a repeat download request.
        # If the ZIP file is complete, we can just use it for the download immediately.
        # If is is not complete, this mostly likely indicates a user has clicked a download link
        # repeatedly, or clicked the browser 'reload' button, whilst waiting for the download.
        # Our best option here is to wait and hope the ZIP file is completeted shortly.
        expected_zipfile = os.path.join(download_param_file_location, zip_file_name)
        if not wait_for_zipfile_ready(expected_zipfile):
            # returns false when timed out
            raise RuntimeError("Timed out waiting for ZIP file {} to be created".format(expected_zipfile))
        logging.info("Reusing existing ZIP file {}/{}".format(download_param_file_location, zip_file_name))
    else:
        # the ZIP file does not exist, so we ceate it.
        logging.info("Creating ZIP file {}/{}".format(download_param_file_location, zip_file_name))
        # read params from JSON file on disk containing
        download_param_file_name = "{}.params.json".format(token)
        param_file_path = os.path.join(download_param_file_location, download_param_file_name)
        logging.debug("retrieving download params from {}".format(param_file_path))
        # if the JSON file doesn't exist return a 404
        if not Path(param_file_path).is_file():
            logging.warning(
                "A data download request was made with token {} but {} does not exist. If this is an old token the file may correctly have been deleted.".format(
                    token, param_file_path
                )
            )
            return Response(
                "These data are no longer available for download.  Please make a new data download request",
                content_type="text/plain; charset=UTF-8",
                status=HTTPStatus.NOT_FOUND,
            )
        public_name_to_lane_files = json.loads(read_text_file(param_file_path))

        # the file paths need to be prefixed with the value of environment variable `data_inst_view_environ` and then turned into PosixPath objects
        data_inst_view_environ = DATA_INST_VIEW_ENVIRON[get_authenticated_project()]
        data_inst_view_path = os.environ[data_inst_view_environ]
        for this_public_name in public_name_to_lane_files:
            complete_file_paths = []
            for this_file in public_name_to_lane_files[this_public_name]:
                if "/" == this_file[0]:
                    this_file = str(this_file)[1:]
                complete_file_paths.append(Path(data_inst_view_path, this_file))
            public_name_to_lane_files[this_public_name] = complete_file_paths
        logging.debug("Public name to data files: {}".format(public_name_to_lane_files))

        # create the ZIP archive
        zip_file_location = download_param_file_location
        zip_files(public_name_to_lane_files, basename=zip_file_basename, location=zip_file_location)

    # look for Sanger proxy HTTP headers indicating the hostname as known to the client
    # so this can be used for the data download redirect
    try:
        headers = call_request_headers()
        uri_scheme_hostname = "{}://{}".format(
            ("https" if HTTPS_PORT == int(headers["X-Forwarded-Port"]) else "http"), headers["X-Forwarded-Host"]
        )
    except KeyError:
        # proxy HTTP headers not found -- hopefully not an error, but an request on the internal network
        logging.info(
            "Cannot find Sanger proxy header X-Forwarded-Host and/or X-Forwarded-Port (hopefully this is a request on the internal network?)"
        )
        uri_scheme_hostname = ""

    zip_file_url = "/".join(
        [uri_scheme_hostname, monocle_data.make_download_symlink(cross_institution=True).rstrip("/"), zip_file_name]
    )
    logging.info("Redirecting data download to {}".format(zip_file_url))

    if redirect_wanted:
        # redirect user to the ZIP file download URL
        return Response(
            "Data for these samples are available for download from {}".format(zip_file_url),
            content_type="text/plain; charset=UTF-8",
            status=HTTPStatus.SEE_OTHER,
            headers={"Location": zip_file_url},
        )
    else:
        return call_jsonify({"download location": zip_file_url}), HTTPStatus.OK


def get_metadata_for_download_route(institution_key: str, category: str, status: str):
    """
    Get metadata as CSV for the user to download.
    IMPORTANT: The other endpoints are all (at time of writing...) for consumption by the front end framework.
    This endpiunt differs, we expect it to be reached by the user clicking on a link/button;  the browser
    should deal with the response (e.g. by opening a spreadsheet application and loading the data into it).
    """
    return _metadata_as_csv_response(
        ServiceFactory.sample_data_service(get_authenticated_username()).get_metadata_for_download(
            get_host_name(request), institution_key, category, status
        )
    )


def _metadata_as_csv_response(metadata_for_download):
    if not metadata_for_download["success"]:
        if "not found" == metadata_for_download["error"]:
            http_status = HTTPStatus.NOT_FOUND
            content = metadata_for_download.get("message", "Not Found")
        elif "request" == metadata_for_download["error"]:
            http_status = HTTPStatus.BAD_REQUEST
            content = metadata_for_download.get("message", "Bad Request")
        else:
            http_status = HTTPStatus.INTERNAL_SERVER_ERROR
            content = metadata_for_download.get("message", "Server Error")
        return Response(content, content_type="text/plain; charset=UTF-8", status=http_status)
    else:
        return Response(
            metadata_for_download["content"],
            content_type="text/csv; charset=UTF-8",  # text/csv is correct MIME type, but could try 'application/vnd.ms-excel' for windows??
            headers={"Content-Disposition": 'attachment; filename="{}"'.format(metadata_for_download["filename"])},
            status=HTTPStatus.OK,
        )


def call_jsonify(args) -> str:
    """Split out jsonify call to make testing easier"""
    return jsonify(args)


def call_request_headers():
    """Wraps flask.request.headers to make testing easier"""
    return request.headers


def call_request_args():
    """Wraps flask.request.args to make testing easier"""
    return request.args


def call_request_cookies():
    """Wraps flask.request.cookies to make testing easier"""
    return request.cookies


def write_text_file(filename, content) -> str:
    with open(filename, "w") as textfile:
        textfile.write(content)
    return filename


def read_text_file(filename) -> str:
    with open(filename, "r") as textfile:
        content = textfile.read()
    return content


def wait_for_zipfile_ready(filename) -> bool:
    start_waiting = time()
    if not complete_zipfile(filename):
        if (time() - start_waiting) > 120:
            return False
        logging.debug("waiting for ZIP file {} to be completed".format(filename))
        sleep(6)
    return True


def get_host_name(req_obj):
    return req_obj.host


def get_authenticated_username():
    """Return the request authenticated user name or throw an UnauthorisedException if one is not present"""
    username = None
    if not ServiceFactory.TEST_MODE:
        try:
            auth_token = call_request_cookies().get(os.environ[AUTH_COOKIE_NAME_ENVIRON])
            username = ServiceFactory.authentication_service().get_username_from_token(auth_token)
            logging.info(
                "{} cookie = {}, username = {}".format(os.environ[AUTH_COOKIE_NAME_ENVIRON], auth_token, username)
            )
        except KeyError:
            msg = "Auth cookie name not defined in environment:  variable {} missing".format(AUTH_COOKIE_NAME_ENVIRON)
            logger.error(msg)
            raise NotAuthorisedException(msg)
        # this will catch missing/empty cookie as well as missing/empty username
        if not username:
            msg = "Username could not be retrieved; auth token = {}".format(auth_token)
            logger.error(msg)
            raise NotAuthorisedException(msg)

    return username


def get_authenticated_project():
    """Return the user's project"""
    user_details = ServiceFactory.user_service(get_authenticated_username()).user_details
    project_list = user_details.get("projects")
    if project_list is None or 0 == len(project_list):
        raise RuntimeError("User accounts must have a projects attribute (user record: {})".format(user_details))
    elif len(project_list) > 1:
        raise RuntimeError(
            "Multiple project membership for users is not currently supported (user record: {})".format(user_details)
        )
    return project_list[0]


def get_metadata_input_default(property_name=None):
    """Return defaults for API #/components/schemas/GetMetadataInput properties.
    If a property name is passed, its default value is returned.
    If nothing is passed, as dict of all defaults is returned.
    (The OpenAPI spec. provides defaults, but these are not passed when a request provides no value)"""

    # get the defaults from the OpenAPI spec.
    default_values = _get_defaults_from_spec(OPENAPI_SPEC_FILE, GET_METADATA_INPUT_SCHEMA)

    # default columns must be retrieved from sample_data_service.get_field_attributes()
    # but this is only necessary if the property asked for was a list of default columns
    # (incl. when nothing specific is asked for and the whole dict is returned)
    if property_name is None or property_name in ["metadata columns", "in silico columns", "qc data columns"]:
        default_columns = _get_default_columns()
        for default_column_type in default_columns:
            default_values[default_column_type] = default_columns[default_column_type]

    if property_name is None:
        return default_values
    return default_values.get(property_name, None)


def _get_defaults_from_spec(openapi_file_name, schema_name):
    """Pass OpenAPI spec. file name and a schmema name.
    Returns all defined default values for properties in the schema.
    Does not currently follow refs."""
    with open(openapi_file_name) as openapi_yaml_file:
        openapi_spec = yaml.safe_load(openapi_yaml_file.read())

    default_values = {}
    properties = openapi_spec["components"]["schemas"][schema_name]["properties"]
    for this_prop in properties:
        this_default = properties[this_prop].get("default")
        if this_default is not None:
            default_values[this_prop] = this_default

    return default_values


def _get_default_columns():
    field_attributes = ServiceFactory.sample_data_service(get_authenticated_username()).get_field_attributes()
    default_columns = {}
    for this_field_type in field_attributes:
        # FIXME this is a really ugly way to get the name of a default columns property from a field type:-/
        default_key = "{} columns".format(this_field_type)
        default_columns[default_key] = []
        for this_category in field_attributes[this_field_type]["categories"]:
            for this_field in this_category.get("fields", []):
                if this_field.get("default", False):
                    default_columns[default_key].append(this_field["name"])
        logging.info("{} default columns: {}".format(default_key, default_columns[default_key]))
    return default_columns


def _parse_BulkDownloadInput(BulkDownloadInput):
    """Parse the BulkDownloadInput request body passed to a POST request handler"""
    sample_filters = BulkDownloadInput["sample filters"]  # required
    assemblies = BulkDownloadInput.get("assemblies", False)
    annotations = BulkDownloadInput.get("annotations", False)
    reads = BulkDownloadInput.get("reads", False)
    return (sample_filters, assemblies, annotations, reads)
