from   collections            import defaultdict
from   csv                    import QUOTE_NONE, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_ALL
from   datetime               import datetime
from   dateutil.relativedelta import relativedelta
import logging
from   os                     import environ
import pandas
from   pathlib                import Path
import urllib.parse
import uuid
import yaml
import urllib.request
import urllib.error

import DataSources.sample_metadata
import DataSources.metadata_download
import DataSources.sequencing_status
import DataSources.pipeline_status
import DataSources.user_data

class MonocleUser:
   """
   Provides a wrapper for claasses the retrieve user details
   Only use this after authentication: trying to get details of users that are not in LDAP will raise an exception
   """
   
   def __init__(self, authenticated_username=None, set_up=True):
      self.updated      = datetime.now()
      self.user_data    = DataSources.user_data.UserData(set_up=set_up)
      # only attempt to load if set_up flag is true
      if authenticated_username is not None and set_up:
         self.load_user_record(authenticated_username)

   def load_user_record(self, authenticated_username):
      self.record = self.user_data.get_user_details(authenticated_username)
      return self.record


class MonocleData:
   """
   Provides wrapper for classes that query various data sources for Monocle data.
   This class exists to convert data between the form in which they are provided by the data sources,
   and whatever form is most convenient for rendering the dashboard.
   """
   sample_table_inst_key   = 'submitting_institution_id'
   # these are the sequencing QC flags from MLWH that are checked; if any are false the sample is counted as failed
   # keys are the keys from the JSON the API giuves us;  strings are what we display on the dashboard when the failure occurs.
   sequencing_flags        = {'qc_lib':   'library',
                              'qc_seq':   'sequencing',
                              }
  
   # format of timestamp returned in MLWH queries
   mlwh_datetime_fmt    = '%Y-%m-%dT%H:%M:%S%z'
   
   # date from which progress is counted
   day_zero = datetime(2019,9,17)

   def __init__(self, set_up=True):
      self.user_record                 = None
      self.institutions_data           = None
      self.samples_data                = None
      self.sequencing_status_data      = None
      self.institution_db_key_to_dict  = {} # see get_institutions for the purpose of this
      # set_up flag causes data objects to be loaded on instantiation
      # only set to False if you know what you're doing
      if set_up:
         self.updated                     = datetime.now()
         self.sample_metadata             = DataSources.sample_metadata.SampleMetadata()
         self.metadata_source             = DataSources.metadata_download.MetadataDownload()
         self.sequencing_status_source    = DataSources.sequencing_status.SequencingStatus()
         self.pipeline_status             = DataSources.pipeline_status.PipelineStatus()
         self.download_symlink_config     = 'data_sources.yml'

   def get_progress(self):
      institutions_data = self.get_institutions()
      total_num_samples_received_by_month = defaultdict(int)
      total_num_lanes_sequenced_by_month  = defaultdict(int)
      progress             = {   'date'             : [],
                                 'samples received'   : [],
                                 'samples sequenced'  : [],
                                 }
      # get number of samples received and number of lanes sequenced during each month counted from "day zero"
      for this_institution in institutions_data.keys():
         # samples received
         this_institution_num_samples_received_by_date = self.num_samples_received_by_date(this_institution)
         for this_date_string in this_institution_num_samples_received_by_date.keys():
            this_date      = datetime.fromisoformat( this_date_string )
            #days_elapsed   = (this_date - self.day_zero).days
            months_elapsed = ((this_date.year - self.day_zero.year) * 12) + (this_date.month - self.day_zero.month)
            total_num_samples_received_by_month[months_elapsed] += this_institution_num_samples_received_by_date[this_date_string]
         # lanes sequenced
         this_institution_num_lanes_sequenced_by_date = self.num_lanes_sequenced_by_date(this_institution)
         for this_date_string in this_institution_num_lanes_sequenced_by_date.keys():
            this_date      = datetime.fromisoformat( this_date_string )
            months_elapsed = ((this_date.year - self.day_zero.year) * 12) + (this_date.month - self.day_zero.month)
            total_num_lanes_sequenced_by_month[months_elapsed] += this_institution_num_lanes_sequenced_by_date[this_date_string]
      # get cumulative numbers received/sequenced for *every* month from 0 to most recent month for which we found something
      num_samples_received_cumulative  = 0
      num_lanes_sequenced_cumulative   = 0
      project_months_elapsed = ((self.updated.year - self.day_zero.year) * 12) + (self.updated.month - self.day_zero.month)
      for this_month_elapsed in range(0, project_months_elapsed+1, 1):
         if this_month_elapsed in total_num_samples_received_by_month:
            num_samples_received_cumulative += total_num_samples_received_by_month[this_month_elapsed]
         if this_month_elapsed in total_num_lanes_sequenced_by_month:
            num_lanes_sequenced_cumulative += total_num_lanes_sequenced_by_month[this_month_elapsed]
         #progress['date'].append( this_month_elapsed )
         progress['date'].append( (self.day_zero + relativedelta(months=this_month_elapsed)).strftime('%b %Y') )
         progress['samples received'].append(  num_samples_received_cumulative )
         progress['samples sequenced'].append( num_lanes_sequenced_cumulative  )
      return progress

   def get_institutions(self):
      """
      Returns a dict of institutions.
      
      {  institution_1   => { 'name':     'the institution name',
                              'db_key':   'db key'
                              }
         institution_2...
         }
         
      If .user_record is defined, it will be used to filter the institutions for those the user belongs to.
            
      Dict keys are alphanumeric-only and safe for HTML id attr. The monocle db keys are not
      suitable for this as they are full institution names.   It's useful to be able to lookup
      a dict key from a db key (i.e. institution name) so MonocleData.institution_db_key_to_dict
      is provided.
      
      ***IMPORTANT***
      Institution IDs (`cn`) are now in LDAP, as are their names.
      We need to stop reading institutions from monocledb, and read the names and IDs from LDAP
      The IDs from LDAP will be used as the dict keys in the code in this module, and we can
      then deprecate `institution_name_to_dict_key()`
      *During the transition* the IDs used in LDAP will be the same as the values returned by
      `institution_name_to_dict_key()`
      
      The data are cached so this can safely be called multiple times without
      repeated monocle db queries being made.
      """
      if self.institutions_data is not None:
         return self.institutions_data
      names = self.sample_metadata.get_institution_names()
      if self.user_record is not None:
         user_memberships = [ inst['inst_id'] for inst in self.user_record['memberOf'] ]
         logging.info("user {} is a member of {}".format( self.user_record['username'],user_memberships))
      institutions = {}
      for this_name in names:
         dict_key = self.institution_name_to_dict_key(this_name, institutions.keys())
         # filter out institution that the user is a member of
         if self.user_record is None or dict_key in user_memberships:
            # currently the db uses insitution names as keys, but we don't want to rely on that
            # so the name and db key are stored as separate items
            # TODO we will start to use the metadata API instread of the database, so this problem will go away soon
            #      (this reckless prediction made 2021-06-15)
            this_db_key = this_name
            institutions[dict_key] = { 'name'   : this_name,
                                       'db_key' : this_db_key
                                       }
            # this allows lookup of the institution dict key from a db key
            self.institution_db_key_to_dict[this_db_key] = dict_key
      self.institutions_data = institutions
      return self.institutions_data

   def get_samples(self):
      """
      Pass dict of institutions. Returns a dict of all samples for each institution in the dict.
      
      {  institution_1   => [sample_id_1, sample_id_2...],
         institution_2...
         }
         
      All institutions are included in the top level dict, even if they have no
      has no samples in the monocle db; the value will be an empty list.
      
      Note that samples in the monocle db derive from an inventory of those that are expected;
      they are not necessarily all present in MLWH, so certain samples may not be found
      in the data returned methods that look for sequencing or pipeline status data.  Think
      of the lists returned by this method as being "all samples IDs that you MIGHT be able to
      retrieve data for".

      The data are cached so this can safely be called multiple times without
      repeated monocle db queries being made.
      """
      if self.samples_data is not None:
         return self.samples_data
      if self.institutions_data is None:
         self.institutions_data = self.get_institutions()
      all_juno_samples = self.sample_metadata.get_samples()
      samples = { i:[] for i in list(self.institutions_data.keys()) }
      for this_sample in all_juno_samples:
         try:
            this_institution_key = self.institution_db_key_to_dict[ this_sample[self.sample_table_inst_key] ]
            this_sample.pop(self.sample_table_inst_key, None)
            samples[this_institution_key].append( this_sample )
         except KeyError:
            logging.info("samples excluded because {} is not in current user's institutions list".format(this_sample[self.sample_table_inst_key]))
      self.samples_data = samples
      return self.samples_data
            
   def get_sequencing_status(self):
      """
      Pass dict of institutions.
      Returns dict with sequencing data for each institution; data are in
      a dict, keyed on the sample ID
      
      Note that these are sample IDs that were found in MLWH, and have therefore
      been processed at Sanger; some samples that are in the monocle db may not
      be present here.
      
      {  institution_1: {  sample_id_1: { seq_data_1 => 'the value',
                                          seq_data_2 => 'the value',
                                          seq_data_3...
                                          },
                           sample_id_2...
                           },
         institution_2...
         }
         
      All institutions are included in the top level dict, even if they have no
      has no samples in the monocle db; the sequencing data for these in an empty dict.
      If a sample from the monocle db has no sequencing data available, that sample's
      ID will not appear as a key in the dict of sequencing data for its institution.
      
      The data are cached so this can safely be called multiple times without
      repeated MLWH queries being made.
      """
      if self.sequencing_status_data is not None:
         return self.sequencing_status_data
      samples_data = self.get_samples()
      institutions_data = self.get_institutions()
      sequencing_status = {}
      for this_institution in institutions_data.keys():
         sequencing_status[this_institution] = {}
         sample_id_list = [ s['sample_id'] for s in samples_data[this_institution] ]
         if 0 < len(sample_id_list)-1:
            logging.debug("{}.get_sequencing_status() requesting sequencing status for samples {}".format(__class__.__name__,sample_id_list))
            try:
               sequencing_status[this_institution] = self.sequencing_status_source.get_multiple_samples(sample_id_list)
               sequencing_status[this_institution]['_ERROR'] = None
            except urllib.error.HTTPError:
               logging.error("{}.get_sequencing_status() failed to collect samples {} for unknown reason".format(__class__.__name__,sample_id_list))
               sequencing_status[this_institution]['_ERROR'] = 'HTTPError: records could not be collected from MLWH'
      self.sequencing_status_data = sequencing_status
      return self.sequencing_status_data

   def get_batches(self):
      """
      Pass dict of institutions. Returns dict with details of batches delivered.
      
      TO DO:  find out a way to get the genuine total number of expected samples for each institution
      """ 
      samples = self.get_samples()
      institutions_data       = self.get_institutions()
      sequencing_status_data  = self.get_sequencing_status()
      batches = { i:{} for i in institutions_data.keys() }
      for this_institution in institutions_data.keys():
         # this ought to be the totalnumber of samples expected from an institution during the JUNO project
         # but currently all we know are the number of samples for which we have metadata; this will be
         # a subset of the total expected samples (until the last delivery arrives) so it isn't what we really want
         # but we have no other data yet
         # this is a check to make sure the data for this institution has actually been found
         if sequencing_status_data[this_institution]['_ERROR'] is not None:
            batches[this_institution] = { '_ERROR' : 'HTTPError: records could not be collected from MLWH' }
            continue
         num_samples_expected          = len(samples[this_institution])
         # this is a list of the samples actually found in MLWH; it is not necessarily the same as
         # the list of sample IDs in the monocle db
         samples_received              = sequencing_status_data[this_institution].keys()
         # this is a dict of the number of samples received on each date; keys are YYYY-MM-DD
         num_samples_received_by_date  = self.num_samples_received_by_date(this_institution)
         # work out the number of samples in each delivery
         # assumption: treat all samples received on a given date as single delivery
         #             this is an approximation: one actual batch might have dates that span two (or a few?) days?
         deliveries = []
         delivery_counter = 0
         for this_date in num_samples_received_by_date.keys():
            delivery_counter += 1
            deliveries.append(  {   'name'   : 'Batch {}'.format(delivery_counter),
                                    'date'   : this_date,
                                    'number' : num_samples_received_by_date[this_date],
                                    },
                                 )
         batches[this_institution] = { '_ERROR'    : None,
                                       'expected'  : num_samples_expected,
                                       'received'  : len(samples_received) - 1,
                                       'deliveries': deliveries,
                                       }
      return batches
      
   def sequencing_status_summary(self):
      """
      Returns dict with a summary of sequencing outcomes for each institution.
      
      {  institution_1: {  'received':    <int>,
                           'completed':   <int>,
                           'success':     <int>,
                           'failed':      <int>,
                           'fail_messages':  [  {  'lane':  lane_id_1,
                                                   'stage': 'name of QC stage where issues was detected',
                                                   'issue': 'string describing the issue'
                                                   },
                                                ...
                                                ],
                           },
         institution_2...
         }

      TO DO:  improve 'failed' dict 'issue' strings
      """
      institutions_data = self.get_institutions()
      sequencing_status_data = self.get_sequencing_status()
      status = {}
      for this_institution in sequencing_status_data.keys():
         if sequencing_status_data[this_institution]['_ERROR'] is not None:
            status[this_institution] = { '_ERROR' : 'HTTPError: records could not be collected from MLWH' }
            continue
         sample_id_list = sequencing_status_data[this_institution].keys()
         status[this_institution] = {  '_ERROR'    : None,
                                       'received'  : len(sample_id_list)-1,
                                       'completed' : 0,
                                       'success'   : 0,
                                       'failed'    : 0,
                                       'fail_messages' : [],
                                       }
         if 0 < len(sample_id_list)-1:
            this_sequencing_status_data = sequencing_status_data[this_institution]
            for this_sample_id in sample_id_list:
               if this_sample_id == '_ERROR' :
                  continue
               # if a sample is in MLWH but there are no lane data, it means sequencing hasn't been done yet
               # i.e. only samples with lanes need to be looked at by the lines below
               for this_lane in this_sequencing_status_data[this_sample_id]['lanes']:
                  if 'qc complete' == this_lane['run_status'] and this_lane['qc_complete_datetime'] and 1 == this_lane['qc_started']:
                     # lane has completed, whether success or failure
                     status[this_institution]['completed'] += 1
                     # look for any failures; note one lane could have more than one failure
                     this_lane_failed = False
                     for this_flag in self.sequencing_flags.keys():
                        if not 1 == this_lane[this_flag]:
                           this_lane_failed = True
                           # record message for this failure
                           status[this_institution]['fail_messages'].append(
                              {  'lane': "{} (sample {})".format(this_lane['id'], this_sample_id),
                                 'stage': self.sequencing_flags[this_flag],
                                 'issue': 'sorry, failure mesages cannot currently be seen here',
                                 },
                              )
                     # count lane either as a success or failure
                     if this_lane_failed:
                        status[this_institution]['failed'] += 1
                     else:
                        status[this_institution]['success'] += 1
      return status

   def pipeline_status_summary(self):
      """
      Returns dict with summary of the pipeline outcomes for each institution.

      {  institution_1: {  'running':     <int>,
                           'success':     <int>
                           'failed':      <int>,
                           'completed':   <int>,
                           'fail_messages':  [  {  'lane':  lane_id_1,
                                                   'stage': 'name of QC stage where issues was detected',
                                                   'issue': 'string describing the issue'
                                                   },
                                                ...
                                                ],
                           },
         institution_2...
         }
         
      Note that when self.pipeline_status is instantiated it creates a dataframe with
      the data, rather than querying an API, there is no separate method to "get" pipeline
      data and it isn't cached -- which is a bit dofferent to how institution/samples/sequencing data
      are handled in this class.
         
      TO DO:  decide what to do about about 'failed' dict 'issue' strings
      """
      institutions_data = self.get_institutions()
      sequencing_status_data = self.get_sequencing_status()
      status = {}
      for this_institution in institutions_data.keys():
         if sequencing_status_data[this_institution]['_ERROR'] is not None:
            status[this_institution] = { '_ERROR' : 'HTTPError: records could not be collected from MLWH' }
            continue
         status[this_institution] = {  '_ERROR'    : None,
                                       'running'   : 0,
                                       'completed' : 0,
                                       'success'   : 0,
                                       'failed'    : 0,
                                       'fail_messages' : [],
                                       }
         sample_id_list = sequencing_status_data[this_institution].keys()
         for this_sample_id in sample_id_list:
            if this_sample_id == '_ERROR':
               continue
            this_sample_lanes = sequencing_status_data[this_institution][this_sample_id]['lanes']
            for this_lane_id in [ lane['id'] for lane in this_sample_lanes ]:
               this_pipeline_status = self.pipeline_status.lane_status(this_lane_id)
               # if the lane failed, increment failed and completed counter
               if this_pipeline_status['FAILED']:
                  status[this_institution]['failed'] += 1
                  status[this_institution]['completed'] += 1
                  # check each stage of the pipeline...
                  for this_stage in self.pipeline_status.pipeline_stage_fields:
                     # ...and if the stage failed...
                     if this_pipeline_status[this_stage] == self.pipeline_status.stage_failed_string:
                        # ...record a message for the failed stage
                        status[this_institution]['fail_messages'].append(  
                           {  'lane'   : "{} (sample {})".format(this_lane_id, this_sample_id),
                              'stage'  : this_stage,
                              # currently have no way to retrieve a failure report
                              'issue'  : 'sorry, failure mesages cannot currently be seen here',
                              },           
                           )
               # if not failed, but succeded, increment success and completed counter
               elif this_pipeline_status['SUCCESS']:
                  status[this_institution]['success'] += 1
                  status[this_institution]['completed'] += 1
               # if neither succeeded nor failed, must still be running
               else:
                  status[this_institution]['running'] += 1
      return status

   def get_metadata_for_download(self, download_hostname, institution, category, status):
      """
      Pass Flask request object, institution name, category ('sequencing' or 'pipeline')
      and status ('successful' or 'failed');
      this identifies the lanes for which metadata are required.
      
      *Note* this was originally written as a method for retrieving sample metadata, but the
      in silico data are now also included so these can all be viewed in a single spreadsheet.
      
      On success, returns content for response, with suggested filename
      
      {  'success'   : True,
         'filename'  : 'the-institution-name_the-category_the-status.csv',
         'content'   : 'a,very,long,multi-line,CSV,string'
         }
         
      On failure, returns reasons ('request' or 'internal'; could extend in future if required??)
      that can be used to provide suitable HTTP status.
      
      {  'success'   : False,
         'error'     : 'request'
         }

      """
      institution_data = self.get_institutions()
      institution_names = [institution_data[i]['name'] for i in institution_data.keys()]
      if not institution in institution_names:
         logging.error("Invalid request to /download: parameter 'institution' was not a recognized institution name; should be one of: \"{}\"".format('", "'.join(institution_names)))
         return { 'success'   : False,
                  'error'     : 'request',
                  }
      
      institution_download_symlink_url_path = self.make_download_symlink(institution)
      if institution_download_symlink_url_path is None:
         logging.error("Failed to create a symlink for data downloads.")
         return { 'success'   : False,
                  'error'     : 'internal',
                  }
      host_url = 'https://{}'.format(download_hostname)
      # TODO add correct port number
      # not critical as it will always be default (80/443) in production, and default port is available on all current dev instances
      # port should be available as request.headers['X-Forwarded-Port'] but that header isn't present (NGINX proxy config error?)
      download_base_url = '/'.join([host_url, institution_download_symlink_url_path])
      logging.info('Data download base URL = {}'.format(download_base_url))

      csv_response_filename = '{}_{}_{}.csv'.format(  "".join([ch for ch in institution if ch.isalpha() or ch.isdigit()]).rstrip(),
                                                      category,
                                                      status)
      csv_response_string = self.metadata_as_csv(institution, category, status, download_base_url)
      return   {  'success'   : True,
                  'filename'  : csv_response_filename,
                  'content'   : csv_response_string
                  }

   def metadata_as_csv(self,institution,category,status,download_base_url):
      """
      Pass institution name, category ('sequencing' or 'pipeline') and status ('successful' or 'failed');
      this identifies the lanes for which metadata are required.
      Also pass the base URL for the download.  The complete download URL for each lane is this
      base URL with the lane ID appended.
      
      *Note* this was originally written as a method for retrieving sample metadata, but the
      in silico data are now also included so these can all be viewed in a single spreadsheet.

      Returns metadata as CSV
      """
      sequencing_status_data = self.get_sequencing_status()
      institution_data_key = self.institution_db_key_to_dict[institution]
      logging.debug("getting metadata: institution db key {} maps to dict key {}".format(institution,institution_data_key))
         
      # get list of lane IDs for this combo of institution/category/status
      lane_id_list = []
      for this_sample_id in sequencing_status_data[institution_data_key].keys():
         if this_sample_id == '_ERROR':
            if sequencing_status_data[institution_data_key][
               this_sample_id] == 'HTTPError: records could not be collected from MLWH':
               logging.error('getting metadata: httpError records could not be collected for {}'.format(institution))
               raise KeyError("{} has no sample data".format(institution))
            else:
               continue

         for this_lane in sequencing_status_data[institution_data_key][this_sample_id]['lanes']:
            
            if 'qc complete' == this_lane['run_status'] and this_lane['qc_complete_datetime'] and 1 == this_lane['qc_started']:
               # lane completed sequencing, though possibly failed
               this_lane_seq_fail = False
               for this_flag in self.sequencing_flags.keys():
                  if not 1 == this_lane[this_flag]:
                     this_lane_seq_fail = True
                     break
               
               want_this_lane = False
               # we're looking for lanes that completed sequencing...
               if 'sequencing' == category:
                  # ...and were successful; so only want this lane if it did *not* fail
                  if 'successful' == status and not this_lane_seq_fail:
                     want_this_lane = True
                  # ...and failed; so only want this lane if it is a failure
                  elif 'failed' == status and this_lane_seq_fail:
                     want_this_lane = True
               # we're looking for lanes that completed the pipelines...
               elif 'pipeline' == category:
                  ## ...(which means the lane must previously have been sequenced OK)...
                  if not this_lane_seq_fail:
                     this_pipeline_status = self.pipeline_status.lane_status(this_lane['id'])
                     # ...and were successful; so only want this lane if it completed and did *not* fail
                     if 'successful' == status and this_pipeline_status['SUCCESS']:
                        want_this_lane = True
                     # ...and failed; so only want this lane if it is a failure
                     elif 'failed' == status and this_pipeline_status['FAILED']:
                        want_this_lane = True
               if want_this_lane:
                  lane_id_list.append( ':'.join([this_sample_id,this_lane['id']]) )

      logging.info("Found {} lanes from {} with {} status {}".format(len(lane_id_list),institution,category,status))
      
      # retrieve the sample metadata and load into DataFrame
      metadata,metadata_col_order   = self._metadata_download_to_pandas_data(self.metadata_source.get_metadata(lane_id_list))
      metadata_df                   = pandas.DataFrame(metadata)
      
      # add download links to metadata DataFrame
      metadata_df = metadata_df.assign( Download_Link = [ '/'.join( [download_base_url, urllib.parse.quote(pn)] ) for pn in metadata_df['Public_Name'].tolist() ] )
      logging.debug("metadata plus download links DataFrame.head:\n{}".format(metadata_df.head()))

      # if there are any in silico data, these are merged into the metadata DataFrame
      in_silico_data,in_silico_data_col_order = self._metadata_download_to_pandas_data(self.metadata_source.get_in_silico_data(lane_id_list))
      if len(in_silico_data) > 0:
         in_silico_data_df = pandas.DataFrame(in_silico_data)
         logging.debug("in silico data DataFrame.head:\n{}".format(in_silico_data_df.head()))
         # merge with left join on LaneID: incl. all metadata rows, only in silico rows where they match a metadta row
         # validate to ensure lane ID is unique in both dataframes
         metadata_df = metadata_df.merge(in_silico_data_df, left_on='Lane_ID', right_on='Sample_id', how='left', validate="one_to_one")
         del in_silico_data_df
         # add silico data columns to the list
         metadata_col_order = metadata_col_order+in_silico_data_col_order
         
      # list of columns in `metadata_col_order` defines the CSV output
      # remove delete Sample_id -- this is a dupliacte of Lane_ID
      while 'Sample_id' in metadata_col_order:
         metadata_col_order.remove('Sample_id')
      # move public name to first column
      while 'Public_Name' in metadata_col_order:
         metadata_col_order.remove('Public_Name')
      metadata_col_order.insert(0,'Public_Name')
      # put download links in last column
      metadata_col_order.append('Download_Link')
      
      metadata_csv = metadata_df.to_csv(columns=metadata_col_order, index=False, quoting=QUOTE_NONNUMERIC)
      logging.debug("merged metadata and in silico data as CSV:\n{}".format(metadata_csv))
      return metadata_csv
      
   def _metadata_download_to_pandas_data(self, api_data):
      """
      Transforms data returned by MetadataDownload methods into a form that can be loaded by pandas
      Something of this form:
         {"order": 1, "name": "Sanger_Sample_ID",  "value": "a_sammple_id"   }
         {"order": 2, "name": "Other_Field",       "value": "something_else" }
      will become:
         {"Sanger_Sample_ID": "a_sammple_id", "Other_Field": "something_else"}
      and a list of hte column ordering is also created:
         ["Sanger_Sample_ID", "Other_Field"]
      Returns tuple: data_dict,column_order_list
      """
      pandas_data = []
      col_order   = []
      first_row   = True
      for this_row in api_data:
         pandas_row = {}
         # get_metadata returns dicts incl. an item item `order` which should be used to sort columns
         for this_column in sorted(this_row, key=lambda col: (this_row[col]['order'])):
            if first_row:
               col_order.append( this_row[this_column]['name'] )
            # get_metadata returns dicts incl. items `name` and `value`for name & value of each column
            pandas_row[this_row[this_column]['name']] = this_row[this_column]['value']
         pandas_data.append( pandas_row )
         first_row = False
      return pandas_data,col_order
   
   def make_download_symlink(self,target_institution):
      """
      Pass the institution name.
      
      This creates a symlink from the web server download directory to the
      directory in which an institution's sample data (annotations,
      assemblies, reads etc.) can be found.
      
      The symlink has a random name so only someone given the URL will be
      able to access it.
      
      The symlink path (relative to web server document root) is returned.
      """
      download_config_section = 'data_download'
      download_dir_param      = 'web_dir'
      download_url_path       = 'url_path'
      data_inst_view_environ  = 'DATA_INSTITUTION_VIEW'
      # get web server directory, and check it exists
      if not Path(self.download_symlink_config).is_file():
         return self._download_config_error("data source config file {} missing".format(self.download_symlink_config))
      # read config, check required params
      with open(self.download_symlink_config, 'r') as file:
         data_sources = yaml.load(file, Loader=yaml.FullLoader)
         if download_config_section not in data_sources or download_dir_param not in data_sources[download_config_section]:
            return self._download_config_error("data source config file {} does not provide the required parameter {}.{}".format(self.download_symlink_config,download_config_section,download_dir_param))
         download_web_dir  = Path(data_sources[download_config_section][download_dir_param])
         if download_config_section not in data_sources or download_url_path not in data_sources[download_config_section]:
            return self._download_config_error("data source config file {} does not provide the required parameter {}.{}".format(self.download_symlink_config,download_config_section,download_url_path))
         download_url_path  = data_sources[download_config_section][download_url_path]
      if not download_web_dir.is_dir():
         return self._download_config_error("data download web server directory {} does not exist (or not a directory)".format(str(download_web_dir)))
      logging.debug('web server data download dir = {}'.format(str(download_web_dir)))
      # get the "target" directory where the data for the institution is kept, and check it exists
      # (Why an environment variable?  Because this can be set  by docker-compose, and it is a path
      # to a volume mount that is also set up by docker-compose.)
      if data_inst_view_environ not in environ:
         return self._download_config_error("environment variable {} is not set".format(data_inst_view_environ))
      download_host_dir = Path(environ[data_inst_view_environ], self.institution_db_key_to_dict[target_institution])
      if not download_host_dir.is_dir():
         return self._download_config_error("data download host directory {} does not exist (or not a directory)".format(str(download_host_dir)))
      logging.debug('host data download dir = {}'.format(str(download_host_dir)))
      # create a randomly named symlink to present to the user (do..while is just in case the path exists already)
      while True:
         random_name          = uuid.uuid4().hex
         data_download_link   = Path(download_web_dir, random_name)
         download_url_path    = '/'.join([download_url_path, random_name])
         if not data_download_link.exists():
            break
      logging.debug('creating symlink {} -> {}'.format(str(data_download_link),str(download_host_dir)))
      data_download_link.symlink_to(download_host_dir.absolute())
      return download_url_path

   def _download_config_error(self,message):
      """
      Call for errors occurring in make_download_symlink().
      Pass error message, which is logged.
      Always returns None.
      """
      logging.error("Invalid data download config: {}".format(message))
      return None
   
   def institution_name_to_dict_key(self, name, existing_keys):
      """
      Private method that creates a shortened, all-alphanumeric version of the institution name
      that can be used as a dict key and also as an HTML id attr
      """
      key = ''
      for word in name.split():
         if word[0].isupper():
            key += word[0:3]
         if 12 < len(key):
            break
      # almost certain to be unique, but...
      while key in existing_keys:
         key += '_X'
      return(key)


   def num_samples_received_by_date(self, institution):
      sequencing_status_data        = self.get_sequencing_status()
      samples_received              = sequencing_status_data[institution].keys()
      if sequencing_status_data[institution]['_ERROR'] is not None:
         return {}
      num_samples_received_by_date  = defaultdict(int)
      for this_sample_id in samples_received:
         if this_sample_id == '_ERROR':
            continue
         # get date in ISO8601 format (YYYY-MM-DD)
         received_date = datetime.strptime(  sequencing_status_data[institution][this_sample_id]['creation_datetime'],
                                             self.mlwh_datetime_fmt
                                             ).strftime( '%Y-%m-%d' )
         num_samples_received_by_date[received_date] += 1
      return num_samples_received_by_date
   
   def num_lanes_sequenced_by_date(self, institution):
      sequencing_status_data        = self.get_sequencing_status()
      if sequencing_status_data[institution]['_ERROR'] is not None:
         return {}
      samples_received              = sequencing_status_data[institution].keys()
      num_lanes_sequenced_by_date   = defaultdict(int)

      for this_sample_id in samples_received:
         if this_sample_id == '_ERROR':
            continue
         # get each lane (some samples may have non lanes yet)
         for this_lane in sequencing_status_data[institution][this_sample_id]['lanes']:
            # get timestamp for completion (some lanes may not have one yet)
            if 'complete_datetime' in this_lane:
               this_lane['complete_datetime']
               # get date in ISO8601 format (YYYY-MM-DD)
               sequenced_date = datetime.strptime( this_lane['complete_datetime'], self.mlwh_datetime_fmt ).strftime( '%Y-%m-%d' )
               num_lanes_sequenced_by_date[sequenced_date] += 1
      return num_lanes_sequenced_by_date
