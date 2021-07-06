import dash
import dash_html_components
from   dash.dependencies            import Input, Output, State, ALL, MATCH
import flask
from   flask                        import jsonify, request, render_template
from   flask_parameter_validation   import ValidateParameters, Route
import logging
from   os                           import environ
from   pathlib                      import Path
import uuid
import yaml

import MonocleDash.monocleclient
import MonocleDash.components as mc

logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='WARNING')

###################################################data  = MonocleDash.monocleclient.MonocleData()

# first create a Flask server
server = flask.Flask(__name__, static_folder='assets')

###################################################################################################################################
# 
# /download
# 
# Flask route, returns CSV retrieved via MonocleData.get_metadata()

def download_config_error(message):
   logging.error("Invalid data download config: {}".format(message))
   return None

def download_parameter_error(message):
   logging.error("Invalid request to /download: {}".format(message))
   return "Download request was not valid.  {}".format(message), 400

#This creates a symlink from the web server download directory to the
#directory in which an institution's sample data (annotations,
#assemblies, reads etc.) can be found.   The symlink has a random name
#so only someone given the URL will be able to access it.
#Pass the institution name; the symlink path (relative to web server
#document root) is returned.
def make_download_symlink(monocle_data, target_institution):
   data_sources_config     = 'data_sources.yml'
   download_config_section = 'data_download'
   download_dir_param      = 'web_dir'
   data_inst_view_environ  = 'DATA_INSTITUTION_VIEW'
   download_web_dir  = None
   download_host_dir = None
   # get web server directory, and check it exists
   if not Path(data_sources_config).is_file():
      return download_config_error("data source config file {} missing".format(data_sources_config))
   with open(data_sources_config, 'r') as file:
      data_sources = yaml.load(file, Loader=yaml.FullLoader)
      if download_config_section not in data_sources or download_dir_param not in data_sources[download_config_section]:
         return download_config_error("data source config file {} does not provide the required paramter {}.{}".format(data_sources_config,download_config_section,download_dir_param))
      download_web_dir  = Path(data_sources[download_config_section][download_dir_param])
   if not download_web_dir.is_dir():
      return download_config_error("data download web server directory {} does not exist (or not a directory)".format(str(download_web_dir)))
   # TODO reduce this to DEBUG after testing
   logging.warning('web server data download dir = {}'.format(str(download_web_dir)))
   # get the "target" directory where the data for the institution is kept, and check it exists
   if data_inst_view_environ not in environ:
      return download_config_error("environment varibale {} is not set".format(data_inst_view_environ))
   download_host_dir = Path(environ[data_inst_view_environ], monocle_data.institution_db_key_to_dict[target_institution])
   if not download_host_dir.is_dir():
      return download_config_error("data download host directory {} does not exist (or not a directory)".format(str(download_host_dir)))
   # TODO reduce this to DEBUG after testing
   logging.warning('host data download dir = {}'.format(str(download_host_dir)))
   # create a randomly named symlink to present to the user (do..while is just in case the path exists already)
   while True:
      data_download_link = Path(download_web_dir, uuid.uuid4().hex)
      if not data_download_link.exists():
         break
   # TODO reduce this to DEBUG after testing
   logging.warning('creating symlink {} -> {}'.format(str(data_download_link),str(download_host_dir)))
   data_download_link.symlink_to(download_host_dir)
   return str(download_web_dir)


# first bit of path should match the `location` used for nginx proxy config
@server.route('/download/<string:institution>/<string:category>/<string:status>')
@ValidateParameters(download_parameter_error)
def metadata_download(  institution:   str = Route(min_length=5),
                        category:      str = Route(pattern='^(sequencing)|(pipeline)$'),
                        status:        str = Route(pattern='^(successful)|(failed)$'),
                        ):
   data = MonocleDash.monocleclient.MonocleData()
   username = request.headers['X-Remote-User']
   # TODO this message should be dropped to 'info' or 'debug'
   # 'warning' is too high, but I want to watch it for a while...
   logging.warning('X-Remote-User header passed to /download = {}'.format(username))
   user_obj = MonocleDash.monocleclient.MonocleUser(username)
   data.user_record = user_obj.record
   institution_data  = data.get_institutions()
   institution_names = [ institution_data[i]['name'] for i in institution_data.keys() ]
   if not institution in institution_names:
      return download_parameter_error("Parameter 'institution' was not a recognized institution name; should be one of: \"{}\"".format('", "'.join(institution_names)))
   
   institution_download_symlink = make_download_symlink(data,institution)
   if institution_download_symlink is None:
      return "Sample data are temporarily unavailable", 500
   host_url = 'https://{}'.format(request.host)
   # TODO add correct port number
   # not critical as it will always be default (80/443) in production, and default port is available on all current dev instances
   # port should be available as request.headers['X-Forwarded-Port'] but that header isn't present (NGINX proxy config error?)
   download_base_url = '{}/{}/'.format(host_url, institution_download_symlink)
   # TODO reduce this to INFO after testing
   logging.warning('Data download base URL = {}'.format(download_base_url))
   
   csv_response = flask.Response( data.get_metadata(institution,category,status,download_base_url) )
   csv_response.headers['Content-Type']         = 'text/csv; charset=UTF-8' # text/csv is correct MIME type, but could try 'application/vnd.ms-excel' for windows??
   csv_response.headers['Content-Disposition']  = 'attachment; filename="{}_{}_{}.csv"'.format("".join([ch for ch in institution if ch.isalpha() or ch.isdigit()]).rstrip(),
                                                                                               category,
                                                                                               status)
   return csv_response


###################################################################################################################################
# 
# /legacy_dashboard_data
# 
# Flask route, providing a hacky API to retrieve the data displayed on the legacy (Dash framework) dashboard
# 
# IMPORTANT this bypasses the X-Remote_user header check, exposing all institutions' data, so the proxy
# needs to restrict access to this route to the docker network

@server.route('/legacy_dashboard/data/summary/')
def legacy_dashboard():
   legacy_dashboard_data = get_dash_params(check_remote_user=False)
   # remove objects not appropriate to API and/or not serializable
   for unwanted_top_level_key in ['user']:
      legacy_dashboard_data.pop(unwanted_top_level_key, None)
   for unwanted_institution_select_key in ['initially_selected', 'institution_callback_input_id']:
      legacy_dashboard_data['institution_select'].pop(unwanted_institution_select_key, None)
   for unwanted_institution_status_key in ['app', 'updated',
                                           'institution_callback_input_id', 'institution_callback_output_id',
                                           'sequencing_callback_input_type', 'sequencing_callback_output_type',
                                           'pipeline_callback_input_type',  'pipeline_callback_output_type',
                                           'refresh_callback_input_id', 'refresh_callback_output_id']:
      legacy_dashboard_data['institution_status'].pop(unwanted_institution_status_key, None)
   logging.debug("legacy dashboard data returned as {}".format(legacy_dashboard_data))
   # jsonify and return
   return jsonify(legacy_dashboard_data)


###################################################################################################################################
# 
# /upload
# 
# Flask route, displays metadata upload page
# TODO this is just a placeholder, there's no actual upload finctionality here

@server.route('/upload/')
def metadata_upload():
   return render_template('upload.html', title='Monocle metadata upload')
 

###################################################################################################################################
# 
# /dashboard
# 
# this is the main Dash app, not a bog standard Flask route

# create Dash app using the extisting Flask server `server`
# url_base_pathname should match the `location` used for nginx proxy config
app   = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# this are HTML element 'id' attributes that are used for callbacks
# they get passed around as params all over the place so safer to keep them in a dict
# then a typo in the code reults in a KeyError, rather than passing the wrong string
# (which would break the dashboard without raising an excption that's easily traced)
callback_component_ids =   {  'refresh_callback_input_id'         : 'refresh-button',
                              'refresh_callback_output_id'        : 'main-page-container',
                              'institution_callback_input_id'     : 'institution-select',
                              'institution_callback_output_id'    : 'institution-status',
                              'sequencing_callback_input_type'    : 'sequencing-failed-input',
                              'sequencing_callback_output_type'   : 'sequencing-failed-container',
                              'pipeline_callback_input_type'      : 'pipeline-failed-input',
                              'pipeline_callback_output_type'     : 'pipeline-failed-container',
                           }

# get_dash_params() returns all the data required to render the dashboard
# TODO this loads all data every time; allow loading of only what's required
# 
# `check_remote_user` causes the X-Remote-User header to be checked for a
# username; this raises an exception *within a request context* because the
# auth module should always set the header.  The username is used downstream
# to restrict access to data from institutions of which that user is a member.
# 
# set `check_remote_user` to False when getting data for an API call that requires
# data from all institutions, *but* be certain to restrict such API endpoints
# to internal access only!
def get_dash_params(check_remote_user=True):
         
   # get the username when handling a request
   # the `except` bodge is to catch when this method is called at the initial service
   # start up, at which time there's no `request` object as not handling at HTTP request
   username    = None
   user_object = None
   if check_remote_user:
      try:
         try:
            username = request.headers['X-Remote-User']
         except KeyError:
            logging.error("request was made without 'X-Remote-User' HTPP header: auth module shouldn't allow that")
            raise
         logging.info('X-Remote-User header = {}'.format(username))
         user_object = MonocleDash.monocleclient.MonocleUser(username)
      except RuntimeError as e:
         if not 'request context' in str(e):
            raise e
         else:
            logging.debug('outside request context:  no user ID available')
         
   data  = MonocleDash.monocleclient.MonocleData()
   if user_object is not None:
      data.user_record = user_object.record
         
   progress_graph       =  {  'title'              : 'Project Progress',  
                              'data'               : data.get_progress(),
                              'x_col_key'          : 'date',
                              'y_cols_keys'        : ['samples received', 'samples sequenced'],
                              'x_label'            : '',
                              'y_label'            : 'number of samples',
                              }
   institution_select   = {   'institutions'       : data.get_institutions(),
                              'initially_selected' : [], #[sorted(institutions, key=institutions.__getitem__)[0]],
                              'institution_callback_input_id'  : callback_component_ids['institution_callback_input_id'],
                              }
   institution_status   = {   'app'                : app,
                              'updated'            : data.updated,
                              'institutions'       : data.get_institutions(),
                              'batches'            : data.get_batches(),
                              'sequencing_status'  : data.sequencing_status_summary(),
                              'pipeline_status'    : data.pipeline_status_summary(),
                              }
   # add component IDs to institution_status
   for this_id in callback_component_ids.keys():
      institution_status[this_id] = callback_component_ids[this_id]
   return { 'user'               : user_object,
            'progress_graph'     : progress_graph,
            'institution_select' : institution_select,
            'institution_status' : institution_status
            }

def page_content(dash_params=None):
   if dash_params is None:
      dash_params =get_dash_params()
   logging.info("page content (currently selected institutions: {})".format(dash_params['institution_select']['initially_selected']))
   content = dash_html_components.Div(
               children = mc.page_header(             'Monocle',
                                                      logo_url       = app.get_asset_url('JunoLogo.svg'),
                                                      logo_link      = 'https://www.gbsgen.net/',
                                                      logo_text      = 'Juno Project',
                                                      header_links   = {'About'     : 'https://www.gbsgen.net/#about',
                                                                        'Team'      : 'https://www.gbsgen.net/#team',
                                                                        'Partners'  : 'https://www.gbsgen.net/#partners',
                                                                        'News'      : 'https://www.gbsgen.net/#twitterFeed',
                                                                        'Funders'   : 'https://www.gbsgen.net/#funders',
                                                                        }
                                                      ) +
                              mc.button_bar(          app
                                                      ) +
                              mc.sample_progress(     dash_params['progress_graph']
                                                      ) +
                              mc.institution_choice(  dash_params['institution_select']
                                                      ) +
                              mc.institution_status(  dash_params['institution_select']['initially_selected'],
                                                      dash_params['institution_status']
                                                      ) +
                              mc.page_footer(         logo_url    = app.get_asset_url('SangerLogo.9423243b.png'),
                                                      logo_link   = 'https://www.sanger.ac.uk/',
                                                      logo_text   = 'Wellcome Sanger Institute',
                                                      contacts   = { 'Monocle Help'    : 'monocle-help@sanger.ac.uk',
                                                                     'Stephen Bentley' : 'sdb@sanger.ac.uk',
                                                                     },
                                                      )
               )
   return content
   
                                                   
app.layout = dash_html_components.Div(
            id          = callback_component_ids['refresh_callback_output_id'],
            className   = 'main_page_container',
            children    = page_content()
            )

# refresh button:  re-renders entire page content, including new data load
@app.callback(
   Output(  component_id = callback_component_ids['refresh_callback_output_id'], component_property = 'children'  ),
   Input(   component_id = callback_component_ids['refresh_callback_input_id'],  component_property = 'n_clicks'  ),
   State(   callback_component_ids['institution_callback_input_id'],             component_property = 'value'     ),
   prevent_initial_call=True
)
def data_refresh(num_clicks, selected_institutions):
   logging.info("refresh button click (currently selected institutions: {})".format(selected_institutions))
   params_for_refresh = get_dash_params()
   params_for_refresh['institution_select']['initially_selected'] = selected_institutions
   return page_content(dash_params = params_for_refresh)


# this displays the chosen institution status containers when the institution select is updated
@app.callback(
   Output(  component_id = callback_component_ids['institution_callback_output_id'],   component_property = 'children'  ),
   Input(   component_id = callback_component_ids['institution_callback_input_id'],    component_property = 'value'     ),
   prevent_initial_call=True
)
def update_institution_status(selected_institutions):
   logging.info("callback triggered: setting the display property for institution status containers; {} will be visible".format(selected_institutions))
   institution_status_params = get_dash_params()['institution_status']
   logging.info("updated institution status with data loaded at {}".format(str(institution_status_params['updated'])))
   return mc.status_by_institution(selected_institutions, institution_status_params)


# this shows/hides an institution's sequencing failure container when the toggle switch is clicked
@app.callback(
   dash.dependencies.Output(  component_id = {'type': callback_component_ids['sequencing_callback_output_type'],  'index': MATCH},  component_property = 'children'  ),
   dash.dependencies.Input(   component_id = {'type': callback_component_ids['sequencing_callback_input_type'],   'index': MATCH},  component_property = 'value'     ),
   prevent_initial_call=True
)
def update_sequence_failed_table(value):
   logging.debug("callback triggered: sequencing failures toggle switch context = {}".format(dash.callback_context.inputs_list))
   # value of input is Boolean, but the callback context object lets us see which toggle switch was clicked
   this_institution = dash.callback_context.inputs_list[0]['id']['index']
   logging.info("callback triggered: setting display property for sequencing failures table for {} (show = {})".format(this_institution,value))
   return mc.failed_samples_container(this_institution, get_dash_params()['institution_status'], 'sequencing', value)


# this shows/hides an institution's pipeline failure container when the toggle switch is clicked
@app.callback(
   dash.dependencies.Output(  component_id = {'type': callback_component_ids['pipeline_callback_output_type'], 'index': MATCH},  component_property = 'children'  ),
   dash.dependencies.Input(   component_id = {'type': callback_component_ids['pipeline_callback_input_type'],  'index': MATCH},  component_property = 'value'     ),
   prevent_initial_call=True
)
def update_sequence_failed_table(value):
   logging.debug("callback triggered: pipeline failures toggle switch context = {}".format(dash.callback_context.inputs_list))
   # value of input is Boolean, but the callback context object lets us see which toggle switch was clicked
   this_institution = dash.callback_context.inputs_list[0]['id']['index']
   logging.info("callback triggered: setting display property for pipeline failures table for {} (show = {})".format(this_institution,value))
   return mc.failed_samples_container(this_institution, get_dash_params()['institution_status'], 'pipeline', value)


if __name__ == '__main__':
   app.run_server(debug=True, host='0.0.0.0', port='8000')
