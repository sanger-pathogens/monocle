import dash
import dash_html_components as html
from   dash.dependencies import Input, Output, State, ALL, MATCH
import logging

import MonocleDash.monocleclient as api
import MonocleDash.components    as mc

logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='DEBUG')

# url_base_pathname should match the `location` used for nginx proxy config
app      = dash.Dash(__name__, url_base_pathname='/dashboard/')
server   = app.server
api      = api.Mock()

institutions=api.get_institutions()

progress_graph_params      = {   'title'              : 'Project Progress',  
                                 'data'               : api.get_progress(),
                                 'x_col_key'          : 'months',
                                 'y_cols_keys'        : ['samples received', 'samples sequenced'],
                                 'x_label'            : 'months since project start',
                                 'y_label'            : 'number of samples',
                                 }

institution_select_params  =  {  'institutions'       : institutions,
                                 'initially_selected' : [], #[sorted(institutions, key=institutions.__getitem__)[0]],
                                 'institution_callback_input_id'  : 'institution-select',
                                 }

institution_status_params  =  {  'app'                : app,
                                 'institutions'       : institutions,
                                 'batches'            : api.get_batches(),
                                 'sequencing_status'  : api.get_sequencing_status(),
                                 'pipeline_status'    : api.get_pipeline_status(),
                                 'institution_callback_output_id'    : 'institution-status',
                                 'sequencing_callback_input_type'    : 'sequencing-failed-input',
                                 'sequencing_callback_output_type'   : 'sequencing-failed-container',
                                 'pipeline_callback_input_type'      : 'pipeline-failed-input',
                                 'pipeline_callback_output_type'     : 'pipeline-failed-container',
                                 }

app.layout = html.Div(
               className='main_page_container',
               children =  mc.page_header( 'Juno' ) +
                           mc.sample_progress( progress_graph_params ) +
                           mc.institution_choice( institution_select_params  ) +
                           mc.institution_status( institution_select_params['initially_selected'], institution_status_params  ) +
                           mc.page_footer( 'page footer placeholder'  )
               )


# this displays the chosen institution status containers when the institution select is updated
@app.callback(
   Output(  component_id = institution_status_params['institution_callback_output_id'],   component_property = 'children'  ),
   Input(   component_id = institution_select_params['institution_callback_input_id'],    component_property = 'value'     ),
)
def update_institution_status(selected_institutions):
   logging.info("callback triggered: setting the display property for institution status containers; {} will be visible".format(selected_institutions))
   return mc.status_by_institution(selected_institutions, institution_status_params)


# this shows/hides an institution's sequencing failure container when the toggle switch is clicked
@app.callback(
   dash.dependencies.Output(  component_id = {'type': institution_status_params['sequencing_callback_output_type'],  'index': MATCH},  component_property = 'children'  ),
   dash.dependencies.Input(   component_id = {'type': institution_status_params['sequencing_callback_input_type'],   'index': MATCH},  component_property = 'value'     ),
)
def update_sequence_failed_table(value):
   logging.debug("callback triggered: sequencing failures toggle switch context = {}".format(dash.callback_context.inputs_list))
   # value of input is Boolean, but the callback context object lets us see which toggle switch was clicked
   this_institution = dash.callback_context.inputs_list[0]['id']['index']
   logging.info("callback triggered: setting display property for sequencing failures table for {} (show = {})".format(this_institution,value))
   return mc.failed_samples_container(this_institution, institution_status_params, 'sequencing', value)


# this shows/hides an institution's pipeline failure container when the toggle switch is clicked
@app.callback(
   dash.dependencies.Output(  component_id = {'type': institution_status_params['pipeline_callback_output_type'], 'index': MATCH},  component_property = 'children'  ),
   dash.dependencies.Input(   component_id = {'type': institution_status_params['pipeline_callback_input_type'],  'index': MATCH},  component_property = 'value'     ),
)
def update_sequence_failed_table(value):
   logging.debug("callback triggered: pipeline failures toggle switch context = {}".format(dash.callback_context.inputs_list))
   # value of input is Boolean, but the callback context object lets us see which toggle switch was clicked
   this_institution = dash.callback_context.inputs_list[0]['id']['index']
   logging.info("callback triggered: setting display property for pipeline failures table for {} (show = {})".format(this_institution,value))
   return mc.failed_samples_container(this_institution, institution_status_params, 'pipeline', value)


if __name__ == '__main__':
   app.run_server(debug=True, host='0.0.0.0', port='8000')
