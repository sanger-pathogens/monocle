""" Module for all error handler methods """
from flask import Response


def handle_unauthorised(exception):
    """ Handle an unauthorised exception """
    return Response(response=json.dumps({'error': 'User authorisation error'}), status=401, mimetype="application/json")


def handle_user_data_error(exception):
    """ Handle an user data error """
    return Response(response=json.dumps({'error': 'User authorisation error'}), status=401, mimetype="application/json")
