import logging
from flask import jsonify, request, Response
from datetime import datetime
import errno
from http import HTTPStatus
import os
from pathlib import Path
from typing import List
from uuid import uuid4

from dash.api.service.service_factory import ServiceFactory
from dash.api.exceptions import NotAuthorisedException
from utils.file import zip_files, ZIP_SUFFIX


logger = logging.getLogger()

# Testing only
ServiceFactory.TEST_MODE = False

# these are set in the openapi.yml file, but request body doesn't seem to set default values
# to they have to be set by the route :-/
GetMetadataInputDefaults = {  "as csv"             : False,
                              "csv filename"       : "monocle.csv",
                              "in silico"          : False,
                              "num rows"           : 20,
                              "metadata columns"   : ["submitting_institution",
                                                      "public_name",
                                                      "host_status",
                                                      "selection_random",
                                                      "country",
                                                      "collection_year",
                                                      "host_species",
                                                      "isolation_source"],
                              "in silico columns"  : ["ST"],
                              }


def get_user_details_route():
    """ Given a username retrieve all details for that user """
    data = ServiceFactory.user_service(get_authenticated_username(request)).user_details
    response_dict = {
        'user_details': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_batches_route():
    """ Get dashboard batch information """
    data = ServiceFactory.sample_tracking_service(get_authenticated_username(request)).get_batches()
    response_dict = {
        'batches': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_institutions_route():
    """ Get a list of institutions """
    data = ServiceFactory.sample_tracking_service(get_authenticated_username(request)).get_institutions()
    response_dict = {
        'institutions': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_progress_route():
    """ Get dashboard progress graph information """
    data = ServiceFactory.sample_tracking_service(get_authenticated_username(request)).get_progress()
    response_dict = {
        'progress_graph': { 'data': data }
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def sequencing_status_summary_route():
    """ Get dashboard sequencing status summary information """
    data = ServiceFactory.sample_tracking_service(get_authenticated_username(request)).sequencing_status_summary()
    response_dict = {
        'sequencing_status': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def pipeline_status_summary_route():
    """ Get dashboard pipeline status summary information """
    data = ServiceFactory.sample_tracking_service(get_authenticated_username(request)).pipeline_status_summary()
    response_dict = {
        'pipeline_status': data
    }
    return call_jsonify(response_dict), HTTPStatus.OK


def get_metadata_route(body):
    """ Get sample metadata based on standard sample filter  """
    logging.info("endpoint handler {} was passed body = {}".format(__name__,body))
    sample_filters      = body['sample filters']
    return_as_csv       = body.get('as csv',             GetMetadataInputDefaults['as csv'])
    csv_filename        = body.get('csv filename',       GetMetadataInputDefaults['csv filename'])
    metadata_columns    = body.get('metadata columns',   GetMetadataInputDefaults['metadata columns'])
    in_silico_columns   = body.get('in silico columns',  GetMetadataInputDefaults['in silico columns'])
    if return_as_csv:
      # note the metadata CSV here does not include data download URLs
      # this is because the sample filters could match samples from multiple institutions, and download
      # links for multiple institutions are not currently supported with CSV metadata downloads
      return  _metadata_as_csv_response(
                  ServiceFactory.data_service(get_authenticated_username(request)).get_csv_download(csv_filename, sample_filters=sample_filters)
                  )
    else:
      # setting column filter params to '_ALL' means all columns should be returned
      if '_ALL' == metadata_columns[0]:
         metadata_columns = None
      if '_ALL' == in_silico_columns[0]:
         in_silico_columns = None
      metadata = ServiceFactory.data_service(
                     get_authenticated_username(request)).get_metadata(
                        sample_filters,
                        start_row         = body.get('start row', None),
                        num_rows          = body.get('num rows',  GetMetadataInputDefaults['num rows']),
                        include_in_silico = body.get('in silico', GetMetadataInputDefaults['in silico']),
                        metadata_columns  = metadata_columns,
                        in_silico_columns = in_silico_columns)
      return call_jsonify( metadata ), HTTPStatus.OK

def bulk_download_info_route(body):
    """ Get download estimate in reponse to the user's changing parameters on the bulk download page """
    logging.info("endpoint handler {} was passed body = {}".format(__name__,body))
    sample_filters, assemblies, annotations, reads = _parse_BulkDownloadInput(body)
    return call_jsonify(
        ServiceFactory.data_service(get_authenticated_username(request)).get_bulk_download_info(
            sample_filters,
            assemblies=assemblies,
            annotations=annotations,
            reads=reads)
    ), HTTPStatus.OK

def bulk_download_urls_route(body):
    """ Get download links to ZIP files w/ lanes corresponding to the request parameters """
    logging.info("endpoint handler {} was passed body = {}".format(__name__,body))
    sample_filters, assemblies, annotations, reads = _parse_BulkDownloadInput(body)
    monocle_data = ServiceFactory.data_service(get_authenticated_username(request))
    samples = monocle_data.get_filtered_samples(sample_filters)
    public_name_to_lane_files = monocle_data.get_public_name_to_lane_files_dict(
        samples,
        assemblies=assemblies,
        annotations=annotations,
        reads=reads)
    zip_file_basename = uuid4().hex
    zip_file_location = monocle_data.get_zip_download_location()

    if not Path(zip_file_location).is_dir():
        logging.error("data downloads directory {} does not exist".format(zip_file_location))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), zip_file_location)

    logging.debug("Public name to data files: {}".format(public_name_to_lane_files))
    zip_files(
        public_name_to_lane_files,
        basename=zip_file_basename,
        location=zip_file_location
        )
    zip_file_url = '/'.join([
        monocle_data.make_download_symlink(cross_institution=True).rstrip('/'),
        zip_file_basename + ZIP_SUFFIX])

    return call_jsonify({
        'download_urls': [zip_file_url]
    }), HTTPStatus.OK

def get_metadata_for_download_route(institution: str, category: str, status: str):
   """
   Get metadata as CSV for the user to download.
   IMPORTANT: The other endpoints are all (at time of writing...) for consumption by the front end framework.
   This endpiunt differs, we expect it to be reached by the user clicking on a link/button;  the browser
   should deal with the response (e.g. by opening a spreadsheet application and loading the data into it).
   """
   return  _metadata_as_csv_response(
               ServiceFactory.data_service(get_authenticated_username(request)).get_metadata_for_download(get_host_name(request), institution, category, status)
               )
   
def _metadata_as_csv_response(metadata_for_download):
   if not metadata_for_download['success']:
      if 'not found' == metadata_for_download['error']:
         http_status = HTTPStatus.NOT_FOUND
         content     = metadata_for_download.get('message','Not Found')
      elif 'request' == metadata_for_download['error']:
         http_status = HTTPStatus.BAD_REQUEST
         content     = metadata_for_download.get('message','Bad Request')
      else:
         http_status = HTTPStatus.INTERNAL_SERVER_ERROR
         content     = metadata_for_download.get('message','Server Error')
      return Response(  content,
                        content_type   = 'text/plain; charset=UTF-8',
                        status         = http_status
                        )
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

def _parse_BulkDownloadInput(BulkDownloadInput):
   """ Parse the BulkDownloadInput request body passed to a POST request handler """
   sample_filters = BulkDownloadInput['sample filters'] # required
   assemblies  = BulkDownloadInput.get('assemblies',  False)
   annotations = BulkDownloadInput.get('annotations', False)
   reads       = BulkDownloadInput.get('reads',       False)
   return(sample_filters, assemblies, annotations, reads)
