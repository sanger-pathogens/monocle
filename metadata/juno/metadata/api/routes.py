import logging
import uuid
import os
import connexion
from flask import jsonify
from metadata.api.upload_handler import UploadHandler
from metadata.api.download_handler import DownloadHandler
from metadata.api.database.monocle_database_service import MonocleDatabaseService

from injector import inject


logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200


@inject
def update_sample_metadata(body: list, upload_handler: UploadHandler, dao: MonocleDatabaseService):
    """ Upload a spreadsheet to the database """
    try:
        uploaded_file = connexion.request.files['spreadsheet']
    except KeyError as ke:
        logger.error('Missing upload spreadsheet file in request')
        return 'Missing spreadsheet file', HTTP_BAD_REQUEST_STATUS

    spreadsheet_file = '/tmp/{}.xlsx'.format(str(uuid.uuid4()))
    uploaded_file.save(spreadsheet_file)

    try:
        validation_errors = upload_handler.load(spreadsheet_file)
        if len(validation_errors) > 0:
            return jsonify({'errors': validation_errors}), HTTP_BAD_REQUEST_STATUS
        else:
            dao.update_sample_metadata(upload_handler.parse())
    finally:
        os.remove(spreadsheet_file)

    return HTTP_SUCCEEDED_STATUS


@inject
def compare_sample_metadata(body: list, dao: MonocleDatabaseService):
    pass


@inject
def get_download_metadata(body: list, download_handler: DownloadHandler, dao: MonocleDatabaseService):
    """ Download sample metadata from the database """
    keys = body
    try:
        metadata_list = dao.get_download_metadata(keys)
    except ValueError as ve:
        logger.error(str(ve))
        return 'Invalid arguments provided', HTTP_BAD_REQUEST_STATUS

    result = jsonify({'download': download_handler.create_download_response(metadata_list)})

    if len(metadata_list) > 0:
        return result, HTTP_SUCCEEDED_STATUS
    else:
        return result, HTTP_NOT_FOUND_STATUS
