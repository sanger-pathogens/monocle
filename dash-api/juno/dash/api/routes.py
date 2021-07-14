import logging
import connexion
from flask import jsonify
from injector import inject


logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200


def hello_world():
    """ Upload a spreadsheet to the database """

    logger.debug('In method hello_world')

    return HTTP_SUCCEEDED_STATUS
