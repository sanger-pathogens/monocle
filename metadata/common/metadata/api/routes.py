import logging
import os
import re
import uuid

import connexion
from flask import current_app as application
from flask import jsonify, request
from injector import inject
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.download_handlers import DownloadInSilicoHandler, DownloadMetadataHandler, DownloadQCDataHandler
from metadata.api.model.qc_data import QCData
from metadata.api.upload_handlers import UploadInSilicoHandler, UploadMetadataHandler

logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200

UPLOAD_EXTENSION = ".xlsx"

# regex for names allowed for filters; interpolated into SQL, so must prevent injection
# (this is easy in practice, as it only has to match column names we choose to sue the the db schema)
FIELD_NAME_REGEX = "^[a-zA-Z0-9_]+$"


def convert_to_json(samples):
    return jsonify(samples)


@inject
def update_sample_metadata_route(body: list, upload_handler: UploadMetadataHandler):
    """Upload a spreadsheet to the database"""
    try:
        uploaded_file = connexion.request.files["spreadsheet"]
        if not uploaded_file:
            raise KeyError("No upload spreadsheet file found")
    except KeyError:
        logger.error("Missing upload spreadsheet file in request")
        return "Missing spreadsheet file", HTTP_BAD_REQUEST_STATUS

    logger.info("Uploading spreadsheet {}...".format(uploaded_file.filename))

    # when True, checks file names for extensions
    upload_handler.check_file_extension = False

    # Set the file delimiter
    upload_handler.file_delimiter = ","

    # Check the extension...
    if not upload_handler.is_valid_file_type(uploaded_file.filename):
        logger.error(
            "Upload file {} does not have a valid extension, expected one of {}".format(
                uploaded_file.filename, upload_handler.allowed_file_types()
            )
        )
        return (
            "The upload file must be one of the following formats: {}".format(upload_handler.allowed_file_types()),
            HTTP_BAD_REQUEST_STATUS,
        )

    spreadsheet_file = "/tmp/{}-{}".format(str(uuid.uuid4()), uploaded_file.filename)
    logger.info("Saving spreadsheet as {}...".format(spreadsheet_file))
    uploaded_file.save(spreadsheet_file)

    try:
        validation_errors = upload_handler.load(spreadsheet_file)
        if len(validation_errors) > 0:
            return convert_to_json({"errors": validation_errors}), HTTP_BAD_REQUEST_STATUS
        else:
            upload_handler.store()
    finally:
        os.remove(spreadsheet_file)

    return HTTP_SUCCEEDED_STATUS


@inject
def update_in_silico_data_route(body: list, upload_handler: UploadInSilicoHandler):
    """Upload a in silico data to the database"""
    try:
        uploaded_file = connexion.request.files["spreadsheet"]
        if not uploaded_file:
            raise KeyError("No upload spreadsheet file found")
    except KeyError:
        logger.error("Missing upload spreadsheet file in request")
        return "Missing spreadsheet file", HTTP_BAD_REQUEST_STATUS

    logger.info("Uploading spreadsheet {}...".format(uploaded_file.filename))

    # do NOT check these file names for extensions
    upload_handler.check_file_extension = True

    # Set the file delimiter
    upload_handler.file_delimiter = "\t"

    # Check the extension...
    if not upload_handler.is_valid_file_type(uploaded_file.filename):
        logger.error(
            "Upload file {} does not have a valid extension, expected one of {}".format(
                uploaded_file.filename, upload_handler.allowed_file_types()
            )
        )
        return (
            "The upload file must be one of the following formats: {}".format(upload_handler.allowed_file_types()),
            HTTP_BAD_REQUEST_STATUS,
        )

    spreadsheet_file = "/tmp/{}-{}".format(str(uuid.uuid4()), uploaded_file.filename)
    logger.info("Saving spreadsheet as {}...".format(spreadsheet_file))
    uploaded_file.save(spreadsheet_file)

    try:
        validation_errors = upload_handler.load(spreadsheet_file)
        if len(validation_errors) > 0:
            return jsonify({"errors": validation_errors}), HTTP_BAD_REQUEST_STATUS
        else:
            upload_handler.store()
    finally:
        os.remove(spreadsheet_file)

    return HTTP_SUCCEEDED_STATUS


@inject
def update_qc_data_route(body: list, dao: MonocleDatabaseService):
    """Upload a QC data to the database"""
    try:
        qc_data_updates = []
        for update in body:
            qc_data_updates.append(QCData(lane_id=update["lane_id"], rel_abun_sa=update.get("rel_abun_sa", None)))
        if qc_data_updates:
            dao.update_lane_qc_data(qc_data_updates)
        return HTTP_SUCCEEDED_STATUS

    except KeyError as e:
        logging.error(
            "{}\nQC data is missing required value: this should have been blocked by the OpenAPI spec. for this endpoint!".format(
                e
            )
        )
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS


@inject
def compare_sample_metadata(body: list):
    # TODO do we need to compare before we update the db? TBD
    pass


@inject
def get_download_metadata_route(body: list, download_handler: DownloadMetadataHandler):
    """Download sample metadata from the database"""
    keys = body
    try:
        metadata_list = download_handler.read_download_metadata(keys)
    except ValueError as ve:
        logger.error(str(ve))
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS

    result = convert_to_json({"download": download_handler.create_download_response(metadata_list)})

    if len(metadata_list) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def get_download_in_silico_data_route(body: list, download_handler: DownloadInSilicoHandler):
    """Download in silico data from the database"""
    keys = body
    try:
        in_silico_data_list = download_handler.read_download_in_silico_data(keys)
    except ValueError as ve:
        logger.error(str(ve))
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS

    result = convert_to_json({"download": download_handler.create_download_response(in_silico_data_list)})

    if len(in_silico_data_list) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def get_download_qc_data_route(body: list, download_handler: DownloadQCDataHandler):
    """Download QC data from the database"""
    keys = body
    try:
        qc_data_list = download_handler.read_download_qc_data(keys)
    except ValueError as ve:
        logger.error(str(ve))
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS

    result = convert_to_json({"download": download_handler.create_download_response(qc_data_list)})

    if len(qc_data_list) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def delete_all_qc_data_route(dao: MonocleDatabaseService):
    """Delete all QC data to the database"""
    dao.delete_all_qc_data()
    return HTTP_SUCCEEDED_STATUS


@inject
def get_institution_names_route(dao: MonocleDatabaseService):
    """Download all institution names from the database"""
    institutions = dao.get_institution_names()

    result = convert_to_json({"institutions": institutions})

    if len(institutions) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def get_samples_route(dao: MonocleDatabaseService):
    """Download all samples and their metadata from the database"""
    try:
        samples = dao.get_samples()
    except ValueError as ve:
        logger.error(str(ve))
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS

    result = convert_to_json({"samples": samples})

    if len(samples) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def get_samples_filtered_by_metadata_route(body: dict, dao: MonocleDatabaseService):
    """Download sample ids from the database for samples matching the metadata filters passed"""
    filters = {}
    for this_filter in body:
        this_field = this_filter["name"]
        these_values = this_filter["values"]
        if not _validate_field_names([this_field]):
            return 'name "{}" is not a valid metadata field name'.format(this_field), HTTP_BAD_REQUEST_STATUS
        filters[this_field] = these_values

    samples = dao.get_samples_filtered_by_metadata(filters)
    logging.debug("DAO returned sample IDs: {}".format(samples))
    # get_samples_filtered_by_metadata() will return None if it is passed a non-existent field name
    if samples is None:
        return "Invalid field name provided", HTTP_BAD_REQUEST_STATUS

    result = convert_to_json(samples)

    if len(samples) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def get_lanes_filtered_by_in_silico_data_route(body: dict, dao: MonocleDatabaseService):
    """Download lane ids from the database for lanes matching the in silico filters passed"""
    filters = {}
    for this_filter in body:
        this_field = this_filter["name"]
        these_values = this_filter["values"]
        if not _validate_field_names([this_field]):
            return 'name "{}" is not a valid in silico field name'.format(this_field), HTTP_BAD_REQUEST_STATUS
        filters[this_field] = these_values

    lanes = dao.get_lanes_filtered_by_in_silico_data(filters)
    logging.debug("DAO returned lanes IDs: {}".format(lanes))
    # get_lanes_filtered_by_in_silico_data() will return None if it is passed a non-existent field name
    if lanes is None:
        return "Invalid field name provided", HTTP_BAD_REQUEST_STATUS

    result = convert_to_json(lanes)

    if len(lanes) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


@inject
def get_distinct_values_route(body: dict, dao: MonocleDatabaseService):
    """Download distinct values present in the database for certain fields"""
    fields = body["fields"]
    institutions = body["institutions"]
    result = _get_distinct_values_common("metadata", fields, institutions, dao)
    return result


@inject
def get_distinct_in_silico_values_route(body: dict, dao: MonocleDatabaseService):
    """Download distinct values present in the database for certain fields"""
    fields = body["fields"]
    institutions = body["institutions"]
    result = _get_distinct_values_common("in silico", fields, institutions, dao)
    return result


@inject
def get_distinct_qc_data_values_route(body: dict, dao: MonocleDatabaseService):
    """Download distinct values present in the database for certain fields"""
    fields = body["fields"]
    institutions = body["institutions"]
    result = _get_distinct_values_common("qc data", fields, institutions, dao)
    return result


@inject
def get_project_information(dao: MonocleDatabaseService):
    project_links = application.config["project_links"]
    result = convert_to_json({"project": project_links})
    return result, HTTP_SUCCEEDED_STATUS


@inject
def get_institutions(dao: MonocleDatabaseService):
    institutions = dao.get_institutions(request)

    result = convert_to_json({"institutions": institutions})

    if len(institutions) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS


def _get_distinct_values_common(field_type, fields, institutions, dao):
    """Download distinct values present in the database for certain fields"""
    if not _validate_field_names(fields):
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS

    distinct_values = dao.get_distinct_values(field_type, fields, institutions)
    logging.debug("DAO returned distinct values: {}".format(distinct_values))
    # get_distinct_values() will return None if it is passed a non-existent field name
    if distinct_values is None:
        return "Invalid field name provided", HTTP_NOT_FOUND_STATUS

    result = convert_to_json({"distinct values": distinct_values})

    return result, HTTP_SUCCEEDED_STATUS


def _validate_field_names(names):
    try:
        field_names_regex = re.compile(FIELD_NAME_REGEX)
        for this_name in names:
            logging.debug("checking field name {}".format(this_name))
            if not field_names_regex.match(this_name):
                raise ValueError(
                    "field name \"{}\" is not valid (only alphanumerics and '_' may be used)".format(this_name)
                )
            else:
                logging.info('field name "{}" is valid'.format(this_name))
    except ValueError as ve:
        logger.error(str(ve))
        return False

    return True
