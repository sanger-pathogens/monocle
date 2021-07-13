import logging
from flask import request
from flask import jsonify
from dash.api.service.service_factory import ServiceFactory
from dash.api.exceptions import NotAuthorisedException


logger = logging.getLogger()

HTTP_SUCCEEDED_STATUS = 200

# Testing only
ServiceFactory.TEST_MODE = False


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
    data_service = ServiceFactory.data_service(get_authenticated_username(request))
    # TODO This needs completing - may need extra bits from monocledash etc
    """
    institution_data = data_service.get_institutions()
    institution_names = [institution_data[i]['name'] for i in institution_data.keys()]
    if not institution in institution_names:
        return download_parameter_error(
            "Parameter 'institution' was not a recognized institution name; should be one of: \"{}\"".format(
                '", "'.join(institution_names)))

    institution_download_symlink_url_path = make_download_symlink(data, institution)
    if institution_download_symlink_url_path is None:
        return "Sample data are temporarily unavailable", 500
    host_url = 'https://{}'.format(request.host)
    # TODO add correct port number
    # not critical as it will always be default (80/443) in production, and default port is available on all current dev instances
    # port should be available as request.headers['X-Forwarded-Port'] but that header isn't present (NGINX proxy config error?)
    download_base_url = '/'.join([host_url, institution_download_symlink_url_path])
    logging.info('Data download base URL = {}'.format(download_base_url))

    csv_response_string = data_service.get_metadata(institution, category, status, download_base_url)
    csv_response.headers[
        'Content-Type'] = 'text/csv; charset=UTF-8'  # text/csv is correct MIME type, but could try 'application/vnd.ms-excel' for windows??
    csv_response.headers['Content-Disposition'] = 'attachment; filename="{}_{}_{}.csv"'.format(
        "".join([ch for ch in institution if ch.isalpha() or ch.isdigit()]).rstrip(),
        category,
        status)
    return csv_response
    """
    return HTTP_SUCCEEDED_STATUS


def call_jsonify(args) -> str:
    """ Split out jsonify call to make testing easier """
    return jsonify(args)


def get_authenticated_username(req_obj):
    """ Return the request authenticated user name or throw an UnauthorisedException if one is not present """
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
    else:
        username = None

    return username
