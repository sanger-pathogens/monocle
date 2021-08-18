import logging
import uuid
import os
import connexion
from flask import jsonify
from injector import inject
from metadata.lib.upload_handler import UploadMetadataHandler, UploadInSilicoHandler
from metadata.api.download_handler import DownloadHandler
from metadata.api.database.monocle_database_service import MonocleDatabaseService


logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200

UPLOAD_EXTENSION = '.xlsx'

def convert_to_json(samples):
    return jsonify(samples)

@inject
def update_sample_metadata(body: list, upload_handler: UploadMetadataHandler):
    """ Upload a spreadsheet to the database """
    try:
        uploaded_file = connexion.request.files['spreadsheet']
        if not uploaded_file:
            raise KeyError('No upload spreadsheet file found')
    except KeyError:
        logger.error('Missing upload spreadsheet file in request')
        return 'Missing spreadsheet file', HTTP_BAD_REQUEST_STATUS

    logger.info('Uploading spreadsheet {}...'.format(uploaded_file.filename))

    # Check the extension...
    if not upload_handler.is_valid_file_type(uploaded_file.filename):
        logger.error('Upload file {} does not have a valid extension, expected one of {}'.format(
            uploaded_file.filename, upload_handler.allowed_file_types()))
        return 'The upload file must be one of the following formats: {}'.format(upload_handler.allowed_file_types()), \
               HTTP_BAD_REQUEST_STATUS

    spreadsheet_file = '/tmp/{}-{}'.format(str(uuid.uuid4()), uploaded_file.filename)
    uploaded_file.save(spreadsheet_file)

    try:
        validation_errors = upload_handler.load(spreadsheet_file)
        if len(validation_errors) > 0:
            return convert_to_json({'errors': validation_errors}), HTTP_BAD_REQUEST_STATUS
        else:
            upload_handler.store()
    finally:
        os.remove(spreadsheet_file)

    return HTTP_SUCCEEDED_STATUS


@inject
def update_in_silico_data(body: list, upload_handler: UploadInSilicoHandler):
    """ Upload a in silico data to the database """
    try:
        uploaded_file = connexion.request.files['spreadsheet']
        if not uploaded_file:
            raise KeyError('No upload spreadsheet file found')
    except KeyError:
        logger.error('Missing upload spreadsheet file in request')
        return 'Missing spreadsheet file', HTTP_BAD_REQUEST_STATUS

    logger.info('Uploading spreadsheet {}...'.format(uploaded_file.filename))

    # Check the extension...
    if not upload_handler.is_valid_file_type(uploaded_file.filename):
        logger.error('Upload file {} does not have a valid extension, expected one of {}'.format(
            uploaded_file.filename, upload_handler.allowed_file_types()))
        return 'The upload file must be one of the following formats: {}'.format(upload_handler.allowed_file_types()), \
               HTTP_BAD_REQUEST_STATUS

    spreadsheet_file = '/tmp/{}-{}'.format(str(uuid.uuid4()), uploaded_file.filename)
    uploaded_file.save(spreadsheet_file)

    try:
        validation_errors = upload_handler.load(spreadsheet_file)
        if len(validation_errors) > 0:
            return jsonify({'errors': validation_errors}), HTTP_BAD_REQUEST_STATUS
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
def get_download_metadata(body: list, download_handler: DownloadHandler):
    """ Download sample metadata from the database """
    keys = body
    try:
        metadata_list = download_handler.read_download_metadata(keys)
    except ValueError as ve:
        logger.error(str(ve))
        return 'Invalid arguments provided', HTTP_BAD_REQUEST_STATUS

    result = convert_to_json({'download': download_handler.create_download_response(metadata_list)})

    if len(metadata_list) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS

@inject
def get_institution_names(dao: MonocleDatabaseService):
    """ Download all institution names from the database """
    institutions = dao.get_institution_names()

    result = convert_to_json({'institutions': institutions})

    if len(institutions) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS

@inject
def get_samples(dao: MonocleDatabaseService):
    """ Download all samples and their metadata from the database """
    samples = dao.get_samples()

    result = convert_to_json({'samples': samples})

    if len(samples) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS

@inject
def get_institutions(dao: MonocleDatabaseService):

    institutions = dao.get_institutions()

    result = convert_to_json({'institutions': institutions})

    if len(institutions) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS
