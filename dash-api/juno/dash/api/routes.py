import logging
from flask import jsonify, request, Response
from dash.api.service.service_factory import ServiceFactory
from dash.api.exceptions import NotAuthorisedException


logger = logging.getLogger()

HTTP_SUCCEEDED_STATUS = 200
HTTP_BAD_REQUEST_STATUS = 400
HTTP_SERVER_ERROR_STATUS = 500

# Testing only
ServiceFactory.TEST_MODE = False


def get_user_details():
    """ Given a username retrieve all details for that user """
    data = ServiceFactory.user_service(get_authenticated_username(request)).user_details
    response_dict = {
        'user_details': data
    }
    return call_jsonify(response_dict), HTTP_SUCCEEDED_STATUS


def get_batches():
    """ Get dashboard batch information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).get_batches()
    response_dict = {
        'batches': data
    }
    return call_jsonify(response_dict), HTTP_SUCCEEDED_STATUS


def get_institutions():
    """ Get a list of institutions """
    data = ServiceFactory.data_service(get_authenticated_username(request)).get_institutions()
    response_dict = {
        'institutions': data
    }
    return call_jsonify(response_dict), HTTP_SUCCEEDED_STATUS


def get_progress():
    """ Get dashboard progress graph information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).get_progress()
    progress_dict = dict()
    # TODO check which of the following values are needed
    #      `data` defintely required
    #      the other values were originally returned by this function for
    #      use in a plot.ly js graph drawing function, and may not be required
    #      by the new dashboard
    progress_dict['title'] = 'Project Progress'
    progress_dict['data'] = data
    progress_dict['x_col_key'] = 'date'
    progress_dict['x_label'] = ''
    progress_dict['y_cols_keys'] = ['samples received', 'samples sequenced']
    progress_dict['y_label'] = 'number of samples'
    response_dict = {
        'progress_graph': progress_dict
    }
    return call_jsonify(response_dict), HTTP_SUCCEEDED_STATUS


def sequencing_status_summary():
    """ Get dashboard sequencing status summary information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).sequencing_status_summary()
    response_dict = {
        'sequencing_status': data
    }
    return call_jsonify(response_dict), HTTP_SUCCEEDED_STATUS


def pipeline_status_summary():
    """ Get dashboard pipeline status summary information """
    data = ServiceFactory.data_service(get_authenticated_username(request)).pipeline_status_summary()
    response_dict = {
        'pipeline_status': data
    }
    return call_jsonify(response_dict), HTTP_SUCCEEDED_STATUS


def get_metadata_for_download(institution: str, category: str, status: str):
   """
   Get metadata as CSV for the user to download.
   IMPORTANT: The other endpoints are all (at time of writing...) for consumption by the front end framework.
   This endpiunt differs, we expect it to be reached by the user clicking on a link/button;  the browser
   should deal with the response (e.g. by opening a spreadsheet application and loading the data into it).
   """
   csv_metadata_response = ServiceFactory.data_service(get_authenticated_username(request)).get_metadata_for_download(get_host_name(request), institution, category, status)
   if not csv_metadata_response['success']:
      if 'request' == csv_metadata_response['error']:
         return HTTP_BAD_REQUEST_STATUS
      else:
         return HTTP_SERVER_ERROR_STATUS
   else:
      return Response( csv_metadata_response['content'], headers = csv_metadata_response['headers'] )

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
