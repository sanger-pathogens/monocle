""" Module for all error handler methods """
from flask import Response


def handle_unauthorised(exception):
    """ Handle an unauthorised exception """
    return Response(response='User authorisation error', status=403, mimetype="text/plain")


def handle_user_data_error(exception):
    """ Handle an user data error """
    return Response(response='User authorisation error', status=403, mimetype="text/plain")
