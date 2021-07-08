import logging
import pandas
from   pandas import DataFrame, read_csv
import yaml

# class DataSourceParamError(Exception):
#    """ exception when data source methods are called with invalid parameter(s) """
#    pass

class PipelineStatus:
   """ provides access to pipeline status data """
   
   data_sources_config     = 'data_sources.yml'
   data_source             = 'pipeline_status'
   pipeline_lane_field     = 'Name'
   stage_done_string       = 'Done'
   stage_failed_string     = 'Failed'
   stage_null_string       = '-'
   # these are the pipeline stages we'd like information about
   pipeline_stage_fields   = ['Import','QC','Assemble','Annotate']

   def __init__(self, config=None):
      if config is None:
         config = self.data_sources_config
      with open(config, 'r') as file:
         data_sources = yaml.load(file, Loader=yaml.FullLoader)
         this_source  = data_sources[self.data_source]
      self.csv_file = this_source['csv_file']
      self.populate_dataframe(self.csv_file)

   def populate_dataframe(self, csv_filename):
      logging.info("reading pipeline status data from {}".format(csv_filename))
      with open(csv_filename, 'r') as csv:
         self.dataframe = pandas.read_csv(csv).set_index(self.pipeline_lane_field)
      logging.debug(self.dataframe)
      return self.dataframe
      
   def lane_status(self, lane_id):
      assert (self.dataframe is not None), "lane_status() called before dataframe was populated"
      logging.debug("extracting pipeline status data for lane {}".format(lane_id))
      status_data = {'FAILED':False, 'SUCCESS':False, }
      num_stages_done = 0
      for this_field in self.pipeline_stage_fields:
         try:
            this_value = self.dataframe.loc[lane_id, this_field]
         except KeyError:
            this_value=None
         # if a value was read...
         if this_value is not None:
            # convert "null" string to `None`
            if this_value == self.stage_null_string:
               this_value=None
            # any occurrence of the "failed" string sets FAILED flag
            elif this_value == self.stage_failed_string:
               # if any stage fails, flag lane as failed
               status_data['FAILED'] = True
               logging.debug("   found failed status for {} stage".format(this_field))
            # the "done" string increments the count of stages done
            elif this_value == self.stage_done_string:
               num_stages_done += 1
         status_data[this_field] = this_value
      # if all stages are done, flag lane as completed successfully
      if len(self.pipeline_stage_fields) == num_stages_done:
         status_data['SUCCESS'] = True
         logging.debug("   all stages are '{}'".format(self.stage_done_string))
      logging.debug("   lane status: {}".format(status_data))
      return status_data
