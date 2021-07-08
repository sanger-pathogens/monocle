import logging
from flask import jsonify, make_response
from injector import inject
from dash.api.user.user_service import UserService, UserDataError


logger = logging.getLogger()

HTTP_BAD_REQUEST_STATUS = 400
HTTP_NOT_FOUND_STATUS = 404
HTTP_SUCCEEDED_STATUS = 200


@inject
def get_user_details(username: str, service: UserService):
    """ Given a username retrieve all details for that user """
    try:
        user_data = service.get_user_details(username)
    except UserDataError as e:
        return make_response(str(e), HTTP_BAD_REQUEST_STATUS)

    return call_jsonify(user_data), HTTP_SUCCEEDED_STATUS


def call_jsonify(*args, **kwargs) -> str:
    """ Split out jsonify call to make testing easier """
    return jsonify(args, kwargs)
