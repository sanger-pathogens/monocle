import logging
from flask import jsonify
from metadata.api.database.monocle_database_service import MonocleDatabaseService

from injector import inject

logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200


@inject
# The parameter name "body" is important - bit dodgy!
def update_sample_metadata(body: list, dao: MonocleDatabaseService):
    pass


@inject
# The parameter name "body" is important - bit dodgy!
def compare_sample_metadata(body: list, dao: MonocleDatabaseService):
    pass


@inject
# The parameter name "body" is important - bit dodgy!
def get_download_metadata(body: list, dao: MonocleDatabaseService):

    keys = body
    try:
        downloads = dao.get_download_metadata(keys)
    except ValueError as ve:
        logger.error(str(ve))
        return "Invalid arguments provided", HTTP_BAD_REQUEST_STATUS

    # Keep in mind that with using jsonify, if you change a model property name it will
    # change the corresponding response json field name. This introduces some
    # coupling but it's quick and sufficient for the moment.
    result = jsonify({'download': downloads})
    print(result)

    if len(downloads) > 0:
        return result
    else:
        return result, HTTP_NOT_FOUND_STATUS
