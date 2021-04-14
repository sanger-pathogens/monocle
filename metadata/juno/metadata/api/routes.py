import logging
from flask import jsonify
from metadata.api.database.monocle_database_service import MonocleDatabaseService

from injector import inject

logger = logging.getLogger()

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
    downloads = dao.get_download_metadata(keys)

    result = jsonify({'download': downloads})
    print(result)

    if len(downloads) > 0:
        return result
    else:
        return result, HTTP_NOT_FOUND_STATUS
