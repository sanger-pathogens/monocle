import logging
from flask import jsonify
from injector import inject
from dash.api.user.user_service import UserService


logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200


def hello_world():
    """ Upload a spreadsheet to the database """

    logger.debug('In method hello_world')

    return HTTP_SUCCEEDED_STATUS


@inject
def get_user_details(username: str, service: UserService):
    """ Give a username retrieve all details for that user """
    user_data = service.get_user_details(username)

    return build_response(user_data), HTTP_SUCCEEDED_STATUS


def build_response(*args, **kwargs) -> str:
    return jsonify(args, kwargs)
