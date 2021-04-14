import dash_core_components   as dcc
import dash_daq               as daq
import dash_html_components   as html
import plotly.express         as px
from   markupsafe             import escape
import logging
import urllib.parse

raquo = '\u00bb'

###################################################################################################################################
# 
#  main sections of the page
# 


def page_header(text):
   elements = [
      html.H1(
         className   = 'page_header',
         children    = [text],
         )
      ]
   return elements


def page_footer(text):
   elements = [
      html.Div(
         className   = 'page_footer',
         children    = [text],
         )
      ]
   return elements
   

def sample_progress(params):
   elements = [   html.Div(id          =  'juno-project-progress',
                           className   = 'sample_progress_container',
                           children    =  [html.H2(children=[params['title']])] +
                                          sample_time_series_graph(params)
                           )
                  ]
   return elements


def institution_choice(params):
   if not isinstance(params['institutions'], dict):
      raise TypeError( "params.institutions is {}, should be a dict".format(type(params['institutions'])) )
   logging.info("rendering institution choice widget")
   elements = [   html.Div(className   = 'institution_select_container',
                           children    = [
                                             html.Label('Select an institution:'),
                                             dcc.Dropdown(
                                                id       = params['institution_callback_input_id'],
                                                options  = [   {'value': k, 'label': params['institutions'][k]['name']}
                                                               for k in sorted( params['institutions'].keys() )
                                                               ],
                                                value    = params['initially_selected'],
                                                multi    = True
                                                ),                              
                                          ]
                           ),
                  html.Br( className = 'clear_float' ),
                  ]

   return elements


def institution_status(initially_selected, params):
   logging.info("rendering institution status container; {} initially selected".format(initially_selected))
   elements =  [  html.Div(id          =  params['institution_callback_output_id'],
                           className   =  'institution_status_container',
                           ),
                  html.Br(className = 'clear_float'),
                  ]
   return elements


###################################################################################################################################
# 
#  project progress components
# 

def sample_time_series_graph(params):
   if not isinstance(params['y_cols_keys'], list):
      raise TypeError( "params.y_cols_keys is {}, should be a list".format(type(params['y_cols_keys'])) )
   for k in [params['x_col_key']]+params['y_cols_keys']:
      if not isinstance(params['data'][k], list):
         raise TypeError( "params.data.{} is {}, should be a list".format(e,type(data[k])) )
   logging.info("rendering time series graph")
   elements = [
                  dcc.Graph(  className   = 'progress_graph',
                              figure      = px.line(  params['data'],
                                                      x  = params['x_col_key'],
                                                      y  = params['y_cols_keys'],
                                                      labels      = {'value':params['y_label'], 'variable': ''},
                                                      line_shape  = 'linear',
                                                      color_discrete_sequence = ['deepskyblue','mediumblue','midnightblue','black'],
                                                      ),
                              )
                  ]
   return elements


###################################################################################################################################
# 
#  project progress components
# 

def status_by_institution(selected_institutions, params):
   for required_dict in ['institutions', 'batches', 'sequencing_status', 'pipeline_status']:
      if not isinstance(params[required_dict], dict):
         raise TypeError( "params.{} is {}, should be a dict".format(required_dict,type(params[required_dict])) )
   params['display'] = {}
   for institution_key in params['institutions'].keys():
      if institution_key in selected_institutions:
         params['display'][institution_key] = 'inherit'
      else:
         params['display'][institution_key] = 'none'
   logging.info("rendering {} institution status".format(selected_institutions))
   elements =  [
                  html.Div(id          =  '{}-status'.format(this_institution),
                           style       =  {'display': params['display'][this_institution]},
                           children    =  [ html.H2( params['institutions'][this_institution]['name'] ) ]   +
                                          samples_received_by_institution(  this_institution, params)       +
                                          samples_sequenced_by_institution( this_institution, params)       +
                                          pipeline_by_institution(          this_institution, params)       +
                                          [ html.Br(className = 'clear_float') ]                            +
                                          failed_samples_by_institution( this_institution, params)          +
                                          [ html.Br(className = 'clear_float') ],
                           )
                  for this_institution in sorted( params['institutions'].keys() )
                  ]
   return elements


###################################################################################################################################
# 
#  samples progress components
# 

def samples_received_by_institution(this_institution, params):
   logging.info("rendering {} samples received".format(this_institution))
   elements = [   html.Div(
                     id          = '{}-batches-table'.format(this_institution),
                     className   = 'samples_received_by_institution_container',
                     children    = samples_received_table(this_institution,params),
                     )
               ]
   return elements


def samples_received_table(this_institution, params):
   this_batch = params['batches'][this_institution]
   if not isinstance(this_batch, dict):
      raise TypeError( "params.batches.{} is {}, should be a dict".format(k,type(this_batch)) )
   for required_int in ['expected', 'received']:
      if not isinstance(this_batch[required_int], int):
         raise TypeError( "params.batches.{}.{} is {}, should be a int".format(k,required_int,type(this_batch[required_int])) )
   if not isinstance(this_batch['deliveries'], list):
      raise TypeError( "params.batches.{}.deliveries is {}, should be a list".format(k,type(this_batch['deliveries'])) )
   for this_delivery in this_batch['deliveries']:
      if not isinstance(this_delivery, dict):
         raise TypeError( "params.batches.{}.deliveries contains a {}, should be a dict".format(k,type(this_delivery)) )
   elements = [   html.Table(
                     className   = 'samples_received_table',
                     children    = [   html.Caption('Samples Received'),
                                       html.Tbody([
                                          html.Tr([
                                             html.Td(
                                                colSpan     = 3,
                                                className   = 'status_desc',
                                                children    = ['Of the ~{} samples expected:'.format(this_batch['expected'])],
                                                ),
                                             html.Td( 
                                                rowSpan     = len(this_batch['deliveries'])+2,
                                                className   = 'per_cent_gauge',
                                                children    = progress_gauge(this_batch['received'], this_batch['expected']),
                                                ),
                                             ])
                                          ]+[
                                             # this row repeated for each batch
                                             html.Tr( children = [
                                                         html.Td( b['name'],   className = 'text_column' ),
                                                         html.Td( b['date'],   className = 'text_column' ),
                                                         html.Td( b['number'], className='numeric' ),
                                                         ]
                                                      )
                                             for b in this_batch['deliveries']
                                          ]+[
                                          html.Tr([
                                             html.Td( 'total received:', colSpan=2, className = 'text_column centered' ),
                                             html.Td( this_batch['received'], className='numeric' ),
                                             ]),
                                          ]),
                                       ]
                     )
                  ]
   return elements


###################################################################################################################################
# 
#  sequencing status components
# 

def samples_sequenced_by_institution(this_institution, params):
   logging.info("rendering {} sequencing status".format(this_institution))
   elements = [   html.Div(
                     id          = '{}-sequenced-table'.format(this_institution),
                     className   = 'samples_sequenced_by_institution_container',
                     children    = samples_sequenced_table(this_institution,params),
                     )
               ]
   return elements

def samples_sequenced_table(this_institution, params):
   this_status = params['sequencing_status'][this_institution]
   if not isinstance(this_status, dict):
      raise TypeError( "params.status.{} is {}, should be a dict".format(k,type(this_status)) )
   for required_int in ['received', 'completed']:
      if not isinstance(this_status[required_int], int):
         raise TypeError( "params.status.{}.{} is {}, should be a int".format(this_institution,required_int,type(this_status[required_int])) )
   if not isinstance(this_status['failed'], list):
      raise TypeError( "params.status.{}.failed is {}, should be a list".format(this_institution,type(this_status['failed'])) )
   # some elements are not displayed if there are no related samples
   if 1 == len(this_status['failed']):
      logging.warn(  "{}: completed = {}, failed = {}, success = {}".format(  this_institution,
                                                                              this_status['completed'],
                                                                              this_status['failed'],
                                                                              (this_status['completed']-len(this_status['failed']))
                                                                              )
                     )
   if not this_status['completed']-len(this_status['failed']) > 0:
      display_success_download = 'none'
   else:
      display_success_download = 'table-cell'
   if not len(this_status['failed']) > 0:
      toggle_disabled         = True;
      display_failed_download = 'none';
   else:
      toggle_disabled         = False;
      display_failed_download = 'table-cell';
   elements = [   html.Table(
                     className   = 'samples_sequenced_table',
                     children    = [   html.Caption('Sequencing Status'),
                                       html.Tbody([
                                          html.Tr([
                                             html.Td(
                                                colSpan     = 4,
                                                className   = 'status_desc',
                                                children    = ['Of the {} samples received:'.format(this_status['received'])],
                                                ),
                                             html.Td( 
                                                rowSpan     = 5,
                                                className   = 'per_cent_gauge',
                                                children    = progress_gauge(this_status['completed'], this_status['received']),
                                                ),
                                             ]),
                                          html.Tr([
                                             html.Td( 'Pending', colSpan  = 2, className = 'text_column' ),
                                             html.Td( this_status['received']-this_status['completed'], className='numeric' ),
                                             html.Td(), # no download currently
                                             ]),
                                          html.Tr([
                                             html.Td( 'Completed', colSpan  = 2, className = 'text_column' ),
                                             html.Td( this_status['completed'], className='numeric' ),
                                             html.Td(), # no download currently
                                             ]),
                                          html.Tr([
                                             html.Td( ),
                                             html.Td( 'Success', className = 'text_column' ),
                                             html.Td( this_status['completed']-len(this_status['failed']), className='numeric' ),
                                             html.Td( download_button(  params['app'],
                                                                        "download {} successfully sequenced samples".format(this_status['completed']-len(this_status['failed'])),
                                                                        params['institutions'][this_institution]['db_key'],
                                                                        'sequencing',
                                                                        'successful',
                                                                        ),
                                                      className   = 'download',
                                                      style       = {'display': display_success_download},
                                                      ),
                                             ]),
                                          html.Tr([
                                             html.Td( ),
                                             html.Td( html.Div(className   = 'aligned_button_container',
                                                               children    = ['Failed ',
                                                                              daq.ToggleSwitch(id           = {'type':  params['sequencing_callback_input_type'],
                                                                                                               'index': this_institution
                                                                                                               },
                                                                                                className   = 'toggle_switch',
                                                                                                disabled    = toggle_disabled,
                                                                                                size        =  30,
                                                                                                value       =  False
                                                                                                ),
                                                                              ],
                                                               ),
                                                      className = 'text_column'
                                                   ),
                                             html.Td( len(this_status['failed']), className='numeric' ),
                                             html.Td( download_button(  params['app'],
                                                                        "download {} failed samples".format(len(this_status['failed'])),
                                                                        params['institutions'][this_institution]['db_key'],
                                                                        'sequencing',
                                                                        'failed',
                                                                        ),
                                                      className   = 'download',
                                                      style       = {'display': display_failed_download},
                                                      ),
                                             ]),
                                          ]),
                                       ]
                     ),
                  ]
   return elements


###################################################################################################################################
# 
#  pipeline status components
# 

def pipeline_by_institution(this_institution, params):
   logging.info("rendering {} pipeline status".format(this_institution))
   elements = [   html.Div(
                     id          = '{}-pipeline-table'.format(this_institution),
                     className   = 'pipeline_by_institution_container',
                     children    = pipeline_table(this_institution,params),
                     )
               ]
   return elements

def pipeline_table(this_institution, params):
   this_status           = params['pipeline_status'][this_institution]
   if not isinstance(this_status, dict):
      raise TypeError( "params.pipeline_status is {}, should be a dict".format(k,type(this_status)) )
   for required_int in ['sequenced', 'running', 'completed']:
      if not isinstance(this_status[required_int], int):
         raise TypeError( "params.pipeline_status.{}.{} is {}, should be a int".format(this_institution,required_int,type(this_status[required_int])) )
   if not isinstance(this_status['failed'], list):
      raise TypeError( "params.pipeline_status.{}.failed is {}, should be a list".format(this_institution,type(this_status['failed'])) )
   # some elements are not displayed/disabled if there are no related samples 
   if not this_status['completed']-len(this_status['failed']) > 0:
      display_success_download = 'none';
   else:
      display_success_download = 'table-cell';
   if not len(this_status['failed']) > 0:
      toggle_disabled         = True;
      display_failed_download = 'none';
   else:
      toggle_disabled         = False;
      display_failed_download = 'table-cell';
   elements = [   html.Table(
                     className   = 'pipeline_table',
                     children    = [   html.Caption('Pipeline Status'),
                                       html.Tbody([
                                          html.Tr([
                                             html.Td(
                                                colSpan     = 4,
                                                className   = 'status_desc',
                                                children    = ['Of the {} samples successfully sequenced:'.format(this_status['sequenced'])]
                                                ),
                                             html.Td( 
                                                rowSpan     = 5,
                                                className   = 'per_cent_gauge',
                                                children    = progress_gauge(this_status['completed'], this_status['sequenced']),
                                                ),
                                             ]),
                                          html.Tr([
                                             html.Td( 'Waiting', colSpan  = 2, className = 'text_column' ),
                                             html.Td( this_status['sequenced']-(this_status['running']+this_status['completed']), className='numeric' ),
                                             html.Td(), # no download currently
                                             ]),
                                          html.Tr([
                                             html.Td( 'Running', colSpan  = 2, className = 'text_column' ),
                                             html.Td( this_status['running'], className='numeric' ),
                                             html.Td(), # no download currently
                                             ]),
                                          html.Tr([
                                             html.Td( 'Completed', colSpan  = 2, className = 'text_column' ),
                                             html.Td( this_status['completed'], className='numeric' ),
                                             html.Td(), # no download currently
                                             ]),
                                          html.Tr([
                                             html.Td( ),
                                             html.Td( 'Success', className = 'text_column' ),
                                             html.Td( this_status['completed']-len(this_status['failed']), className='numeric' ),
                                             html.Td( download_button(  params['app'],
                                                                        "download {} samples successfully processed through the pipeline".format(this_status['completed']-len(this_status['failed'])),
                                                                        params['institutions'][this_institution]['db_key'],
                                                                        'pipeline',
                                                                        'successful',
                                                                        ),
                                                      className   = 'download',
                                                      style       = {'display': display_success_download},
                                                      ),
                                             ]),
                                          html.Tr([
                                             html.Td( ),
                                             html.Td( html.Div(className   = 'aligned_button_container',
                                                               children    = ['Failed ',
                                                                              daq.ToggleSwitch(id           = {'type':  params['pipeline_callback_input_type'],
                                                                                                               'index': this_institution
                                                                                                               },
                                                                                                className   = 'toggle_switch',
                                                                                                disabled    = toggle_disabled,
                                                                                                size        =  30,
                                                                                                value       =  False
                                                                                                ),
                                                                              ],
                                                               ),
                                                      className = 'text_column'
                                                      ),
                                             html.Td( len(this_status['failed']), className='numeric' ),
                                             html.Td( download_button(  params['app'],
                                                                        "download {} failed samples".format(len(this_status['failed'])),
                                                                        params['institutions'][this_institution]['db_key'],
                                                                        'pipeline',
                                                                        'failed',
                                                                        ),
                                                      className   = 'download',
                                                      style       = {'display': display_failed_download},
                                                      ),
                                             ]),
                                          ]),
                                       ]
                     ),
                  ]
   return elements


###################################################################################################################################
# 
#  failed samples components
# 

def failed_samples_by_institution(this_institution, params):
   logging.info("rendering {} failed samples container".format(this_institution))
   elements = [html.Div(id = {'type':params['sequencing_callback_output_type'],  'index':this_institution}),
               html.Div(id = {'type':params['pipeline_callback_output_type'],    'index':this_institution}),
               ]
   return elements


def failed_samples_container(this_institution,params,stage,show):
   if not 'sequencing' == stage and not 'pipeline' == stage:
      raise ValueError( "stage should be  'sequencing' or 'pipeline', not n'{}'".format(stage) )
   key = '{}_status'.format(stage)
   failed_samples = params[key][this_institution]['failed']
   if not isinstance(failed_samples, list):
      raise TypeError( "params.{}.{}.failed is {}, should be a list".format(key,this_institution,type(failed_samples)) )
   if False == show:
      display = 'none'
   else:
      display = 'inherit'
   logging.info("rendering {} rendering {} failures table (display = {})".format(this_institution,stage,display))
   elements = [  html.Div(
                     id          =  '{}-{}-failed-table'.format(this_institution,stage),
                     style       =  {'display': display},
                     className   =  'failed_samples_by_institution_container',
                     children    =  #failed_samples_download(failed_samples, params['app']) +
                                    failed_samples_table('{} Failures'.format(stage.capitalize()), failed_samples)
                     )
                  ]
   return elements


def failed_samples_table(caption,failed_samples):
   if not isinstance(failed_samples, list):
      raise TypeError( "failed_samples is {}, should be a list".format(type(failed_samples)) )
   table_rows =   [  html.Tr([
                        html.Th('Lane'),
                        html.Th('Stage'),
                        html.Th('Issue'),
                        ])
                     ]+[
                        # this row repeated for each failed sample
                        html.Tr( children = [
                                    html.Td( f['lane'] ),
                                    html.Td( f['stage'] ),
                                    html.Td( f['issue'] ),
                                    ]
                                 )
                        for f in failed_samples
                     ]
   elements = [   html.Table(
                     className   = 'failed_samples_table',
                     children    = [   html.Caption(caption),
                                       html.Tbody(table_rows)
                                       ]
                     )
                  ]
   return elements

def failed_samples_download(failed_samples, icon_url):
   if not isinstance(failed_samples, list):
      raise TypeError( "failed_samples is {}, should be a list".format(type(failed_samples)) )
   logging.debug("download icon URL is {}".format(icon_url))
   elements = [   
               html.Div(className   = 'aligned_button_container_inside_failed_sampled_container',
                        children    = download_button('#', icon_url, "download {} failed samples".format(len(failed_samples)))
                        ),
               ]
   return elements


###################################################################################################################################
# 
#  generic components
# 

def progress_gauge(current,total):
   logging.debug("progress gauge: {} of {}".format(current,total))
   try:
      per_cent = round(100*(current/total))
   except ZeroDivisionError:
      per_cent = 0
   # some "total" numbers are estimates, so could go over 100%
   if per_cent > 100:
      per_cent = 100
   elements = [   
                  daq.Gauge(  value          = per_cent,
                              max            = 100,
                              min            = 0,
                              size           = 130,
                              color          = {"gradient"  : True,
                                                "ranges"    : {"red"    : [0,  25],
                                                               "yellow" : [25, 75],
                                                               "green"  : [75, 100],
                                                               },
                                                },
                              label          = {'label' : '%',
                                                'style' : {'font-size': 'larger'}
                                                },
                              labelPosition  = 'bottom',
                              ),
                  ]
   return elements

def download_button(app, alt_text, institution, category, status):
   icon_url          = app.get_asset_url("download-icon.png")
   download_url      = '/download/{}/{}/{}'.format(urllib.parse.quote(institution),
                                                   urllib.parse.quote(category),
                                                   urllib.parse.quote(status),
                                                   )
   download_target   = '{}_{}_{}'.format( escape(institution),
                                          escape(category),
                                          escape(status)
                                          )
   logging.debug("download button: download URL = {}, icon URL = {}, alt text = '{}'".format(download_url, icon_url, alt_text))
   elements = [   
                  html.A(  className   = 'download_link',
                           href        = download_url,
                           target      = download_target,
                           children    = [html.Img(src   = icon_url,
                                                   alt   = alt_text,
                                                   title = alt_text,
                                                   className = 'download_icon',
                                                   ),
                                          ],
                           ),
                  ]
   return elements
