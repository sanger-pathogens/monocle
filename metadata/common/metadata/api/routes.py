import logging
import os
import re
import uuid

import connexion
from flask import current_app as application
from flask import jsonify
from injector import inject
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.download_handlers import DownloadInSilicoHandler, DownloadMetadataHandler, DownloadQCDataHandler
from metadata.api.upload_handlers import UploadInSilicoHandler, UploadMetadataHandler, UploadQCDataHandler

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

    uploaded_file = _get_uploaded_spreadsheet("spreadsheet")
    if uploaded_file is None:
        return "Missing spreadsheet file", HTTP_BAD_REQUEST_STATUS
    logger.info("Uploading spreadsheet {}...".format(uploaded_file.filename))

    upload_handler.check_file_extension = False
    upload_handler.file_delimiter = ","

    # Check the extension...
    file_type_ok, fail_message = _check_spreadsheet_file_type(upload_handler, uploaded_file)
    if not file_type_ok:
        return (fail_message, HTTP_BAD_REQUEST_STATUS)

    spreadsheet_file = _save_spreadsheet(uploaded_file)

    # Validate; if it passes, store it
    try:
        validation_errors = upload_handler.load(spreadsheet_file, connexion.request)
        if len(validation_errors) > 0:
            return convert_to_json({"errors": validation_errors}), HTTP_BAD_REQUEST_STATUS
        else:
            upload_handler.store()
    finally:
        os.remove(spreadsheet_file)

    return HTTP_SUCCEEDED_STATUS


@inject
def update_qc_data_route(body: list, upload_handler: UploadQCDataHandler):
    """Upload a QC data to the database"""
    uploaded_file = _get_uploaded_spreadsheet("spreadsheet")
    if uploaded_file is None:
        return "Missing spreadsheet file", HTTP_BAD_REQUEST_STATUS
    logger.info("Uploading spreadsheet {}...".format(uploaded_file.filename))

    upload_handler.check_file_extension = True
    upload_handler.file_delimiter = "\t"

    # Check the extension...
    file_type_ok, fail_message = _check_spreadsheet_file_type(upload_handler, uploaded_file)
    if not file_type_ok:
        return (fail_message, HTTP_BAD_REQUEST_STATUS)

    spreadsheet_file = _save_spreadsheet(uploaded_file)

    # Validate; if it passes, store it
    try:
        validation_errors = upload_handler.load(spreadsheet_file, connexion.request)
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
    uploaded_file = _get_uploaded_spreadsheet("spreadsheet")
    if uploaded_file is None:
        return "Missing spreadsheet file", HTTP_BAD_REQUEST_STATUS
    logger.info("Uploading spreadsheet {}...".format(uploaded_file.filename))

    upload_handler.check_file_extension = True
    upload_handler.file_delimiter = "\t"

    # Check the extension...
    file_type_ok, fail_message = _check_spreadsheet_file_type(upload_handler, uploaded_file)
    if not file_type_ok:
        return (fail_message, HTTP_BAD_REQUEST_STATUS)

    spreadsheet_file = _save_spreadsheet(uploaded_file)

    # Validate; if it passes, store it
    try:
        validation_errors = upload_handler.load(spreadsheet_file, connexion.request)
        if len(validation_errors) > 0:
            return convert_to_json({"errors": validation_errors}), HTTP_BAD_REQUEST_STATUS
        else:
            upload_handler.store()
    finally:
        os.remove(spreadsheet_file)

    return HTTP_SUCCEEDED_STATUS


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
def get_project_information(dao: MonocleDatabaseService):
    project_links = application.config["project_links"]
    result = convert_to_json({"project": project_links})
    return result, HTTP_SUCCEEDED_STATUS


def _get_uploaded_spreadsheet(file_name_param):
    # returns uploaded spreadsheet file, or None if missing
    try:
        uploaded_file = connexion.request.files[file_name_param]
        if not uploaded_file:
            # file name parameter exists in request (so no KeyError) but no file name actually passed
            logger.error(
                'Request includes the parameter "{}" that should provide the uploaded spreadsheet name, but the value is blank/missing'.format(
                    file_name_param
                )
            )
            return None
    except KeyError:
        logger.error(
            'Request is missing the parameter "{}" that should provide the uploaded spreadsheet name'.format(
                file_name_param
            )
        )
        return None
    return uploaded_file


def _check_spreadsheet_file_type(upload_handler, uploaded_file):
    # check file type
    # return tuple:  flag if file type is OK, and (possibly blank) error message
    type_is_ok = upload_handler.is_valid_file_type(uploaded_file.filename)
    if type_is_ok:
        file_type_ok = True
        message = ""
    else:
        logger.error(
            "Upload file {} does not have a valid extension, expected one of {}".format(
                uploaded_file.filename, upload_handler.allowed_file_types()
            )
        )
        file_type_ok = False
        message = "The upload file must be one of the following formats: {}".format(upload_handler.allowed_file_types())
    return (file_type_ok, message)


def _save_spreadsheet(uploaded_file):
    # save uplooaded spreadsheet to /tmp and return path
    spreadsheet_file = "/tmp/{}-{}".format(str(uuid.uuid4()), uploaded_file.filename)
    logger.info("Saving spreadsheet as {}...".format(spreadsheet_file))
    uploaded_file.save(spreadsheet_file)
    return spreadsheet_file


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
