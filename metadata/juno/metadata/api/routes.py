import logging
import uuid
import os
import connexion
from flask import jsonify
from injector import inject
from metadata.api.upload_handler import UploadHandler
from metadata.api.download_handler import DownloadHandler
from metadata.api.database.monocle_database_service import MonocleDatabaseService


logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200

UPLOAD_EXTENSION = '.xlsx'


@inject
def update_sample_metadata(body: list, upload_handler: UploadHandler):
    """ Upload a spreadsheet to the database """
    try:
        uploaded_file = connexion.request.files['spreadsheet']
        if not uploaded_file:
            raise KeyError('No upload spreadsheet file found')
    except KeyError:
        logger.error('Missing upload spreadsheet file in request')
        return 'Missing spreadsheet file', HTTP_BAD_REQUEST_STATUS

    # Check the extension...
    # TODO File extensions should be externalised to config
    if uploaded_file.filename:
        file_ext = os.path.splitext(uploaded_file.filename)[1]
        if file_ext != UPLOAD_EXTENSION:
            logger.error('Upload file does not have the correct extension: {}'.format(file_ext))
            return 'The upload file must be an Excel spreadsheet {} file'.format(UPLOAD_EXTENSION), \
                   HTTP_BAD_REQUEST_STATUS

    logger.info('Uploading spreadsheet {}...'.format(uploaded_file.filename))

    spreadsheet_file = '/tmp/{}.{}'.format(str(uuid.uuid4()), UPLOAD_EXTENSION)
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

    result = jsonify({'download': download_handler.create_download_response(metadata_list)})

    if len(metadata_list) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS

@inject
def get_institution_names(dao: MonocleDatabaseService):
    """ Download all institution names from the database """
    institutions = dao.get_institution_names()

    result = jsonify({'institutions': institutions})

    if len(institutions) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS

@inject
def get_samples(dao: MonocleDatabaseService):
    """ Download all samples and their metadata from the database """
    samples = dao.get_samples()

    result = jsonify({'download': samples})

    if len(samples) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS

@inject
def get_samples_for_study_id(study_id: int, dao: SequencingDatabaseService):

    samples = dao.get_samples_for_study_id(study_id)

    result = jsonify({'samples': samples})

    if len(samples) > 0:
        return result
    else:
        return result, HTTP_NOT_FOUND_STATUS