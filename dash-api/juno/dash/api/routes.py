import logging
from flask import jsonify, request, Response
from dash.api.service.service_factory import ServiceFactory
from dash.api.exceptions import NotAuthorisedException
from datetime import datetime
from http import HTTPStatus
from typing import List


logger = logging.getLogger()

# Testing only
ServiceFactory.TEST_MODE = False


def get_user_details():
    """ Given a username retrieve all details for that user """
    data = ServiceFactory.user_service(get_authenticated_username(request)).user_details
    response_dict = {
        'user_details': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_batches():
    """ Get dashboard batch information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).get_batches()
    response_dict = {
        'batches': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_institutions():
    """ Get a list of institutions """
    data = ServiceFactory.data_service(get_authenticated_username(request)).get_institutions()
    response_dict = {
        'institutions': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_progress():
    """ Get dashboard progress graph information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).get_progress()
    response_dict = {
        'progress_graph': { 'data': data }
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def sequencing_status_summary():
    """ Get dashboard sequencing status summary information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).sequencing_status_summary()
    response_dict = {
        'sequencing_status': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def pipeline_status_summary():
    """ Get dashboard pipeline status summary information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).pipeline_status_summary()
    response_dict = {
        'pipeline_status': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def bulk_download_info(batches: List[str], assemblies: bool = False, annotations: bool = False, reads: bool = False):
    """ Get download estimate in reponse to the user's changing parameters on the bulk download page """
    return call_jsonify(
        ServiceFactory.data_service(get_authenticated_username(request)).get_bulk_download_info(
            batches,
            assemblies=assemblies,
            annotations=annotations,
            reads=reads)
    ), HTTPStatus.OK


def get_metadata_for_download(institution: str, category: str, status: str):
   """
   Get metadata as CSV for the user to download.
   IMPORTANT: The other endpoints are all (at time of writing...) for consumption by the front end framework.
   This endpiunt differs, we expect it to be reached by the user clicking on a link/button;  the browser
   should deal with the response (e.g. by opening a spreadsheet application and loading the data into it).
   """
   metadata_for_download = ServiceFactory.data_service(get_authenticated_username(request)).get_metadata_for_download(get_host_name(request), institution, category, status)
   if not metadata_for_download['success']:
      if 'request' == metadata_for_download['error']:
         return HTTPStatus.BAD_REQUEST
      else:
         return HTTPStatus.INTERNAL_SERVER_ERROR
   else:
      return Response(  metadata_for_download['content'],
                        content_type   = 'text/csv; charset=UTF-8', # text/csv is correct MIME type, but could try 'application/vnd.ms-excel' for windows??
                        headers        = {'Content-Disposition': 'attachment; filename="{}"'.format(metadata_for_download['filename'])},
                        status         = HTTPStatus.OK
                        )


def call_jsonify(args) -> str:
    """ Split out jsonify call to make testing easier """
    return jsonify(args)


def get_host_name(req_obj):
   return req_obj.host


def get_authenticated_username(req_obj):
    """ Return the request authenticated user name or throw an UnauthorisedException if one is not present """
    username = None
    if not ServiceFactory.TEST_MODE:
        try:
            username = req_obj.headers['X-Remote-User']
            logging.info('X-Remote-User header = {}'.format(username))
        except KeyError:
            pass

        if not username:
            msg = "Request was made without 'X-Remote-User' HTTP header: auth module shouldn't allow that!"
            logger.error(msg)
            raise NotAuthorisedException(msg)

    return username
