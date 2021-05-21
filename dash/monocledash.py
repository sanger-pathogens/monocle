import dash
import dash_html_components
from   dash.dependencies            import Input, Output, State, ALL, MATCH
import flask
from   flask_parameter_validation   import ValidateParameters, Route
import logging

import MonocleDash.monocleclient
import MonocleDash.components as mc

logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='WARNING')

###################################################data  = MonocleDash.monocleclient.MonocleData()

# first create a Flask server
server = flask.Flask(__name__)

def download_parameter_error(message):
   logging.error("Invalid request to /download: {}".format(message))
   return "Download request was not valid.  {}".format(message), 400

# first bit of path should match the `location` used for nginx proxy config
@server.route('/download/<string:institution>/<string:category>/<string:status>')
@ValidateParameters(download_parameter_error)
def index(  institution:   str = Route(min_length=5),
            category:      str = Route(pattern='^(sequencing)|(pipeline)$'),
            status:        str = Route(pattern='^(successful)|(failed)$'),
            ):
   data              = MonocleDash.monocleclient.MonocleData()
   institution_data  = data.get_institutions()
   institution_names = [ institution_data[i]['name'] for i in institution_data.keys() ]
   if not institution in institution_names:
      return download_parameter_error("Parameter 'institution' was not a recognized institution name; should be one of: \"{}\"".format('", "'.join(institution_names)))
   csv_response = flask.Response( data.get_metadata(institution,category,status) )
   csv_response.headers['Content-Type']         = 'text/csv; charset=UTF-8' # text/csv is correct MIME type, but could try 'application/vnd.ms-excel' for windows??
   csv_response.headers['Content-Disposition']  = 'attachment; filename="{}_{}_{}.csv"'.format("".join([ch for ch in institution if ch.isalpha() or ch.isdigit()]).rstrip(),
                                                                                               category,
                                                                                               status)
   return csv_response


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

# TODO this loads all data every time; allow loading of only what's required
def get_dash_params():
   data  = MonocleDash.monocleclient.MonocleData()
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
   return { 'progress_graph'     : progress_graph,
            'institution_select' : institution_select,
            'institution_status' : institution_status
            }

def page_content(dash_params=None):
   if dash_params is None:
      dash_params =get_dash_params()
   logging.info("page content (currently selected institutions: {})".format(dash_params['institution_select']['initially_selected']))
   content = dash_html_components.Div(
               children = mc.page_header(         'Monocle',
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
                              mc.refresh_button(      app.get_asset_url('refresh-icon.png')
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
   logging.info("updated institution status with data loaded at {} ***".format(str(institution_status_params['updated'])))
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
