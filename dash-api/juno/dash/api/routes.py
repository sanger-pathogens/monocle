import   logging
from     flask          import jsonify, request, Response
from     datetime       import datetime
import   errno
from     http           import HTTPStatus
from     http.client    import HTTPS_PORT
from     itertools      import islice
import   json
import   os
from     pathlib        import Path
from     time           import sleep, time
from     typing         import List
from     urllib.error   import HTTPError
from     uuid           import uuid4

from dash.api.service.service_factory  import ServiceFactory
from dash.api.exceptions               import NotAuthorisedException
from dash.api.utils.file               import zip_files, ZIP_SUFFIX, complete_zipfile


logger = logging.getLogger()

# Testing only
ServiceFactory.TEST_MODE = False

DATA_INST_VIEW_ENVIRON  = 'DATA_INSTITUTION_VIEW'

# these are set in the openapi.yml file, but request body doesn't seem to set default values
# to they have to be set by the route :-/
GetMetadataInputDefaults = {  "as csv"             : False,
                              "csv filename"       : "monocle.csv",
                              "in silico"          : True,
                              "qc data"            : True,
                              "num rows"           : 20,
                              "metadata columns"   : ["submitting_institution",
                                                      "public_name",
                                                      "host_status",
                                                      "selection_random",
                                                      "country",
                                                      "collection_year",
                                                      "host_species",
                                                      "isolation_source",
                                                      "serotype"],
                              "in silico columns"  : ["ST"],
                              "qc data columns"    : ["rel_abun_sa"],
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

def get_field_attributes_route():
    data = ServiceFactory.sample_data_service(get_authenticated_username(request)).get_field_attributes()
    response_dict = {
        'field_attributes': data
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
    qc_data_columns     = body.get('qc data columns',    GetMetadataInputDefaults['qc data columns'])
    
    try:
      if return_as_csv:
         # note the metadata CSV here does not include data download URLs
         # this is because the sample filters could match samples from multiple institutions, and download
         # links for multiple institutions are not currently supported with CSV metadata downloads
         return  _metadata_as_csv_response(
                     ServiceFactory.sample_data_service(get_authenticated_username(request)).get_csv_download(csv_filename, sample_filters=sample_filters)
                     )
      else:
         # setting column filter params to '_ALL' means all columns should be returned
         if '_ALL' == metadata_columns[0]:
            metadata_columns = None
         if '_ALL' == in_silico_columns[0]:
            in_silico_columns = None
         if '_ALL' == qc_data_columns[0]:
            qc_data_columns = None
         metadata = ServiceFactory.sample_data_service(
                        get_authenticated_username(request)).get_metadata(
                           sample_filters,
                           start_row         = body.get('start row', None),
                           num_rows          = body.get('num rows',  GetMetadataInputDefaults['num rows']),
                           include_in_silico = body.get('in silico', GetMetadataInputDefaults['in silico']),
                           include_qc_data   = body.get('qc data',   GetMetadataInputDefaults['qc data']),
                           metadata_columns  = metadata_columns,
                           in_silico_columns = in_silico_columns,
                           qc_data_columns   = qc_data_columns)
         if metadata is None:
            return Response(  'No matching samples were found',
                              content_type   = 'text/plain; charset=UTF-8',
                              status         = HTTPStatus.NOT_FOUND
                              )
         return call_jsonify( metadata ), HTTPStatus.OK
    except HTTPError as e:
      if '400' in str(e):
          return 'Bad request', HTTPStatus.BAD_REQUEST
      raise e


def get_distinct_values_route(body):
    """ Return distinct values found in metadata, in silico or QC data fields """
    logging.info("endpoint handler {} was passed body = {}".format(__name__,body))
    monocle_data  = ServiceFactory.sample_data_service(get_authenticated_username(request))
    field_types   = ['metadata', 'in silico', 'qc data']
    
    # validate *types* of field named in request
    fields_types_found = []
    distinct_values_request = {}
    for this_obj in body:
      this_field_type = this_obj['field type']
      if this_field_type in fields_types_found:
         logging.info("{}.get_distinct_values_route() was passed field type {} more than once".format(__name__, this_field_type))
         return "Field type {} was included in the request more than once".format(this_field_type), HTTPStatus.BAD_REQUEST
      if this_field_type not in field_types:
         logging.info("{}.get_distinct_values_route() was passed field type {}: should be one of {}".format(__name__, this_field_type, field_types))
         return "Invalid field type {}: should be one of {}".format(this_field_type, field_types), HTTPStatus.BAD_REQUEST
      fields_types_found.append(this_field_type)
      distinct_values_request[this_field_type] = this_obj['field names']

    distinct_values = monocle_data.get_distinct_values(distinct_values_request)
    
    if distinct_values is None:
    # this means a non-existent field was asked for => customized 404
       return 'One or more of the requested fields could not be found', HTTPStatus.NOT_FOUND

    response_dict = {
        'distinct values': distinct_values
    }
    return call_jsonify( response_dict ), HTTPStatus.OK

def bulk_download_info_route(body):
    """ Get download estimate in reponse to the user's changing parameters on the bulk download page """
    logging.info("endpoint handler {} was passed body = {}".format(__name__,body))
    sample_filters, assemblies, annotations, reads = _parse_BulkDownloadInput(body)
    
    try:
      download_info = ServiceFactory.sample_data_service(get_authenticated_username(request)).get_bulk_download_info(
               sample_filters,
               assemblies=assemblies,
               annotations=annotations,
               reads=reads)
    except HTTPError as e:
      if '400' in str(e):
          return 'Bad request', HTTPStatus.BAD_REQUEST
      raise e
    if download_info is None:
      return Response(  'No matching samples were found',
                        content_type   = 'text/plain; charset=UTF-8',
                        status         = HTTPStatus.NOT_FOUND
                        )
    return call_jsonify(download_info), HTTPStatus.OK

def bulk_download_urls_route(body):
    """ Get download links to ZIP files w/ lanes corresponding to the request parameters """
    logging.info("endpoint handler {} was passed body = {}".format(__name__,body))
    sample_filters, assemblies, annotations, reads = _parse_BulkDownloadInput(body)
    try:
      monocle_data = ServiceFactory.sample_data_service(get_authenticated_username(request))
      samples = monocle_data.get_filtered_samples(sample_filters)
    # catch 404 and 400s from metadata API
    except HTTPError as e:
      if '404' in str(e):
         return Response(  'No matching samples were found',
                           content_type   = 'text/plain; charset=UTF-8',
                           status         = HTTPStatus.NOT_FOUND
                           )
      elif '400' in str(e):
         return 'Bad request', HTTPStatus.BAD_REQUEST
      raise e
   
    public_name_to_lane_files = monocle_data.get_public_name_to_lane_files_dict(
        samples,
        assemblies=assemblies,
        annotations=annotations,
        reads=reads)
    logging.debug("Public name to data files: {}".format(public_name_to_lane_files))

    download_param_file_location = monocle_data.get_bulk_download_location()
    if not Path(download_param_file_location).is_dir():
        logging.error("data downloads directory {} does not exist".format(download_param_file_location))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), download_param_file_location)
    
    # the data we want to serialize contains PosixPath objects that we need to make into strings
    data_inst_view_path = os.environ[DATA_INST_VIEW_ENVIRON]
    for this_public_name in public_name_to_lane_files:
       file_paths_as_strings = []
       for this_file in public_name_to_lane_files[this_public_name]:
          # this slice removes the leading path defined by the environment variable DATA_INST_VIEW_ENVIRON
          # to (a) avoid exposing our file system structure oin plublically accessible file, and
          # (b) ensure downlaods don't break if we move the data to a new directory
          file_paths_as_strings.append( str(this_file)[len(data_inst_view_path):] )
       public_name_to_lane_files[this_public_name] = file_paths_as_strings

    # limit the number of samples to be included in each ZIP archive
    max_samples_per_zip  = body.get('max samples per zip',  None)
    if max_samples_per_zip is not None:
      if reads:
         max_samples_per_zip = int( (max_samples_per_zip/10) + 0.5 )
         if max_samples_per_zip < 1:
            max_samples_per_zip = 1 
    else:
      # if not passed, get value from config file
      max_samples_per_zip = monocle_data.get_bulk_download_max_samples_per_zip(including_reads=reads)
    
    download_url_list = []
    start = 0
    total = len(public_name_to_lane_files)
    num_downloads    = round( (total / max_samples_per_zip + 0.5001) )
    samples_in_each  = round( (total / num_downloads       + 0.5001) )
    while total > start:
      this_zip_archive_contents = dict( islice(public_name_to_lane_files.items(), start, (start+samples_in_each), 1) )
      download_token = uuid4().hex
      download_param_file_name = "{}.params.json".format(download_token)
      file_written = write_text_file(os.path.join(download_param_file_location,download_param_file_name), json.dumps(this_zip_archive_contents))
      logging.debug("wrote download params for samples {} to {} to {}".format((start+1), (start+samples_in_each), file_written))
      download_url_list.append( '/'.join([monocle_data.get_bulk_download_route(), download_token]) )
      start += samples_in_each
      
    return call_jsonify({
        'download_urls': download_url_list
    }), HTTPStatus.OK

def data_download_route(token: str):
    """ Provides download if the ZIP archive providing the data associated with the token passed.
    The token identifies a JSON file that holds the parameter required to create the ZIP archive.
    Unless the ZIP archive exists (i.e. this download has been requsetd before) the ZIP archive is
    created.
    By default 303 response is returned providing a download of the ZIP archive via the static file route;
    but if the query uses `?redirect=false` then the resp[onse is a 200 with the static download
    route in the response body.
    If the JSON file isn't found a 404 is returned (this will happen if the download link that
    was used is old, and the housekeeping cron job has deleted the JSON file in the interim).
    """
    redirect_wanted = 'true' == call_request_args().get('redirect', 'true').lower()
    logging.info("endpoint handler {} was passed token = {} , redirect flag({}) = {}".format(__name__, token, type(redirect_wanted), redirect_wanted))
    monocle_data = ServiceFactory.sample_data_service(get_authenticated_username(request))
    
    logging.info("Data download request headers:\n{}".format(call_request_headers()))
    
    download_param_file_location = monocle_data.get_bulk_download_location()
    if not Path(download_param_file_location).is_dir():
       logging.error("data downloads directory {} does not exist".format(download_param_file_location))
       raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), download_param_file_location)
      
    zip_file_basename = token
    zip_file_name     = zip_file_basename + ZIP_SUFFIX
    if Path(download_param_file_location,zip_file_name).is_file():
      # The ZIP file exists. This means we have a repeat download request.
      # If the ZIP file is complete, we can just use it for the download immediately.
      # If is is not complete, this mostly likely indicates a user has clicked a download link
      # repeatedly, or clicked the browser 'reload' button, whilst waiting for the download.
      # Our best option here is to wait and hope the ZIP file is completeted shortly.
      expected_zipfile = os.path.join(download_param_file_location,zip_file_name)
      if not wait_for_zipfile_ready(expected_zipfile):
        # returns false when timed out
        raise RuntimeError( "Timed out waiting for ZIP file {} to be created".format(expected_zipfile) )
      logging.info("Reusing existing ZIP file {}/{}".format(download_param_file_location,zip_file_name))
    else:
      # the ZIP file does not exist, so wwe ceate it.
      logging.info("Creating ZIP file {}/{}".format(download_param_file_location,zip_file_name))
      # read params from JSON file on disk containing
      download_param_file_name = "{}.params.json".format(token)
      param_file_path = os.path.join(download_param_file_location,download_param_file_name)
      # if the JSON file doesn't exist return a 404
      if not Path(param_file_path).is_file():
         logging.warning(  "A data download request was made with token {} but {} does not exist. If this is an old token the file may correctly have been deleted.".format(
                              token,
                              param_file_path)
                           )
         return Response(  'These data are no longer available for download.  Please make a new data download request',
                           content_type   = 'text/plain; charset=UTF-8',
                           status         = HTTPStatus.NOT_FOUND
                           )
      public_name_to_lane_files = json.loads(read_text_file(param_file_path))
      
      # the file paths need to be prefixed with DATA_INST_VIEW_ENVIRON and then turned into PosixPath objects
      data_inst_view_path = os.environ[DATA_INST_VIEW_ENVIRON]
      for this_public_name in public_name_to_lane_files:
         complete_file_paths = []
         for this_file in public_name_to_lane_files[this_public_name]:
            if '/' == this_file[0]:
               this_file = str(this_file)[1:]
            complete_file_paths.append( Path(data_inst_view_path, this_file) )
         public_name_to_lane_files[this_public_name] = complete_file_paths
      logging.debug("Public name to data files: {}".format(public_name_to_lane_files))
       
      # create the ZIP archive
      zip_file_location = download_param_file_location
      zip_files(
         public_name_to_lane_files,
         basename=zip_file_basename,
         location=zip_file_location
         )
      
    # look for Sanger proxy HTTP headers indicating the hostname as known to the client
    # so this can be used for the data download redirect
    try:
       headers = call_request_headers()
       uri_scheme_hostname = "{}://{}".format(  ('https' if HTTPS_PORT == int(headers['X-Forwarded-Port']) else 'http'),
                                                headers['X-Forwarded-Host']
                                                )
    except KeyError:
       # proxy HTTP headers not found -- hopefully not an error, but an request on the internal network
       logging.info("Cannot find Sanger proxy header X-Forwarded-Host and/or X-Forwarded-Port (hopefully this is a request on the internal network?)")
       uri_scheme_hostname = ''
       
    zip_file_url = '/'.join(  [  uri_scheme_hostname,
                                 monocle_data.make_download_symlink(cross_institution=True).rstrip('/'),
                                 zip_file_name]
                              )
    logging.info("Redirecting data download to {}".format(zip_file_url))
    
    if redirect_wanted:
      # redirect user to the ZIP file download URL
      return Response( "Data for these samples are available for download from {}".format(zip_file_url),
                  content_type   = 'text/plain; charset=UTF-8',
                  status         = HTTPStatus.SEE_OTHER,
                  headers        = {'Location': zip_file_url},
                  )
    else:
      return call_jsonify({'download location': zip_file_url}), HTTPStatus.OK

def get_metadata_for_download_route(institution: str, category: str, status: str):
   """
   Get metadata as CSV for the user to download.
   IMPORTANT: The other endpoints are all (at time of writing...) for consumption by the front end framework.
   This endpiunt differs, we expect it to be reached by the user clicking on a link/button;  the browser
   should deal with the response (e.g. by opening a spreadsheet application and loading the data into it).
   """
   return  _metadata_as_csv_response(
               ServiceFactory.sample_data_service(get_authenticated_username(request)).get_metadata_for_download(get_host_name(request), institution, category, status)
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
 
def call_request_headers():
    """ Wraps flask.request.headers to make testing easier """
    return request.headers

def call_request_args():
    """ Wraps flask.request.args to make testing easier """
    return request.args

def write_text_file(filename, content) -> str:
    with open(filename, 'w') as textfile:
      textfile.write(content)
    return filename
 
def read_text_file(filename) -> str:
    with open(filename, 'r') as textfile:
      content = textfile.read()
    return content
   
def wait_for_zipfile_ready(filename) -> bool:
    start_waiting = time()
    if not complete_zipfile(filename):
      if ( time() - start_waiting ) > 120:
        return False
      logging.debug("waiting for ZIP file {} to be completed".format(filename))
      sleep(6)
    return True
   
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
   sample_filters = BulkDownloadInput['sample filters']  # required
   assemblies     = BulkDownloadInput.get('assemblies',  False)
   annotations    = BulkDownloadInput.get('annotations', False)
   reads          = BulkDownloadInput.get('reads',       False)
   return(sample_filters, assemblies, annotations, reads)
