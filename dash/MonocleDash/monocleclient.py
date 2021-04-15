from   collections            import defaultdict
from   datetime               import datetime
from   dateutil.relativedelta import relativedelta
import logging
import DataSources.monocledb
import DataSources.metadata_download
import DataSources.sequencing_status
import DataSources.pipeline_status

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

   def __init__(self):
      self.monocledb                   = DataSources.monocledb.MonocleDB()
      self.metadata_source             = DataSources.metadata_download.MetadataDownload()
      self.sequencing_status_source    = DataSources.sequencing_status.SequencingStatus()
      self.pipeline_status             = DataSources.pipeline_status.PipelineStatus()
      self.institutions_data           = None
      self.samples_data                = None
      self.sequencing_status_data      = None
      self.institution_db_key_to_dict  = {} # see get_institutions for the purpose of this

   def get_progress(self):
      institutions_data = self.get_institutions()
      total_num_samples_received_by_month = defaultdict(int)
      total_num_lanes_sequenced_by_month  = defaultdict(int)
      max_months_elapsed   = 0
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
            previous_max = max_months_elapsed
            max_months_elapsed = max(months_elapsed,max_months_elapsed)
            total_num_samples_received_by_month[months_elapsed] += this_institution_num_samples_received_by_date[this_date_string]
         # lanes sequenced
         this_institution_num_lanes_sequenced_by_date = self.num_lanes_sequenced_by_date(this_institution)
         for this_date_string in this_institution_num_lanes_sequenced_by_date.keys():
            this_date      = datetime.fromisoformat( this_date_string )
            months_elapsed = ((this_date.year - self.day_zero.year) * 12) + (this_date.month - self.day_zero.month)
            previous_max = max_months_elapsed
            max_months_elapsed = max(months_elapsed,max_months_elapsed)
            total_num_lanes_sequenced_by_month[months_elapsed] += this_institution_num_lanes_sequenced_by_date[this_date_string]
      # get cumulative numbers received/sequenced for *every* month from 0 to most recent month for which we found something
      num_samples_received_cumulative  = 0
      num_lanes_sequenced_cumulative   = 0
      for this_month_elapsed in range(0, max_months_elapsed+1, 1):
         if this_month_elapsed in total_num_samples_received_by_month:
            num_samples_received_cumulative += total_num_samples_received_by_month[this_month_elapsed]
         if this_month_elapsed in total_num_lanes_sequenced_by_month:
            num_lanes_sequenced_cumulative += total_num_lanes_sequenced_by_month[this_month_elapsed]
         #progress['date'].append( this_month_elapsed )
         progress['date'].append( (self.day_zero + relativedelta(months=this_month_elapsed)).strftime('%b %Y') )
         progress['samples received'].append(  num_samples_received_cumulative )
         progress['samples sequenced'].append( num_lanes_sequenced_cumulative  )
      return progress

   def get_institutions(self, pattern=None):
      """
      Returns a dict of institutions.
      
      {  institution_1   => { 'name':     'the institution name',
                              'db_key':   'db key'
                              }
         institution_2...
         }
         
      If option pattern is passed, only institutions with names that include the pattern are returned (case insensitive).
      
      Dict keys are alphanumeric-only and safe for HTML id attr. The monocle db keys are not
      suitable for this as they are full institution names.   It's useful to be able to lookup
      a dict key from a db key (i.e. institution name) so MonocleData.institution_db_key_to_dict
      is provided.
      
      The data are cached so this can safely be called multiple times without
      repeated monocle db queries being made.
      """
      if self.institutions_data is not None:
         return self.institutions_data
      names = self.monocledb.get_institution_names()
      institutions = {}
      for this_name in names:
         if None == pattern or pattern.lower() in this_name.lower():
            dict_key = self.institution_name_to_dict_key(this_name, institutions.keys())
            # currently the db uses insitution names as keys, but we don't want to rely on that
            # so the name and db key are stored as separate items
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
      institutions_data = self.get_institutions()
      all_juno_samples = self.monocledb.get_samples()
      samples = { i:[] for i in list(self.institutions_data.keys()) }
      for this_sample in all_juno_samples:
         this_institution_key = self.institution_db_key_to_dict[ this_sample[self.sample_table_inst_key] ]
         this_sample.pop(self.sample_table_inst_key, None)
         samples[this_institution_key].append( this_sample )
      self.samples_data = samples
      return self.samples_data
            
   def get_sequencing_status(self):
      """
      Pass dict of institutions.
      Returns dict with sequencing data for each institution; data are in
      a dict, keyed on the sample ID
      
      Note that these are sample IDs that were found in MLWH, and have therefore
      neen processed at Sanger; some samples that are in the monocle db may not
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
         if 0 < len(sample_id_list):
            logging.debug("{}.get_sequencing_status() requesting sequencing status for samples {}".format(__class__.__name__,sample_id_list))
            sequencing_status[this_institution] = self.sequencing_status_source.get_multiple_samples(sample_id_list)
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
         batches[this_institution] = { 'expected'  : num_samples_expected,
                                       'received'  : len(samples_received),
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
         sample_id_list = sequencing_status_data[this_institution].keys()
         status[this_institution] = {  'received'  : len(sample_id_list),
                                       'completed' : 0,
                                       'success'   : 0,
                                       'failed'    : 0,
                                       'fail_messages' : [],
                                       }
         if 0 < len(sample_id_list):
            this_sequencing_status_data = sequencing_status_data[this_institution]
            for this_sample_id in sample_id_list:
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
         status[this_institution] = {  'running'   : 0,
                                       'completed' : 0,
                                       'success'   : 0,
                                       'failed'    : 0,
                                       'fail_messages' : [],
                                       }
         sample_id_list = sequencing_status_data[this_institution].keys()
         for this_sample_id in sample_id_list:
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

   def get_metadata(self,institution,category,status):
      """
      Pass institution name, category ('sequencing' or 'pipeline') and status ('successful' or 'failed');
      this identifies the lanes for which metadata are required.
      
      Returns metadata as CSV
      """
      sequencing_status_data = self.get_sequencing_status()
      institution_data_key = self.institution_db_key_to_dict[institution]
      logging.debug("getting metadata: institution db key {} maps to dict key {}".format(institution,institution_data_key))
         
      # get list of lane IDs for this combo of institution/category/status
      lane_id_list = []
      for this_sample_id in sequencing_status_data[institution_data_key].keys():
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
                     if 'successful' == status and this_pipeline_status['COMPLETED']:
                        want_this_lane = True
                     # ...and failed; so only want this lane if it is a failure
                     elif 'failed' == status and this_pipeline_status['FAILED']:
                        want_this_lane = True
               
               if want_this_lane:
                  lane_id_list.append( ':'.join([this_sample_id,this_lane['id']]) )
      
      logging.info("Found {} lanes from {} with {} status {}".format(len(lane_id_list),institution,category,status))
      
      #self.metadata_source.get_metadata(lane_id_list)
      csv = []
      # TODO turn metadata structure into CSV; below is some mock data
      csv = """\"column_one\",\"column_two\",\"column_three\"
\"col 1 row 1\",1.31234,\"some string\"
\"col 1 row 3\",4.32454,\"this, string, has commas\"
\"col 1 row 3\",17.58991,\"another string\"
"""
      return csv


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
      num_samples_received_by_date  = defaultdict(int)
      for this_sample_id in samples_received:
         # get date in ISO8601 format (YYYY-MM-DD)
         received_date = datetime.strptime(  sequencing_status_data[institution][this_sample_id]['creation_datetime'],
                                             self.mlwh_datetime_fmt
                                             ).strftime( '%Y-%m-%d' )
         num_samples_received_by_date[received_date] += 1
      return num_samples_received_by_date
   
   def num_lanes_sequenced_by_date(self, institution):
      sequencing_status_data        = self.get_sequencing_status()
      samples_received              = sequencing_status_data[institution].keys()
      num_lanes_sequenced_by_date   = defaultdict(int)

      for this_sample_id in samples_received:
         # get each lane (some samples may have non lanes yet)
         for this_lane in sequencing_status_data[institution][this_sample_id]['lanes']:
            # get timestamp for completion (some lanes may not have one yet)
            if 'complete_datetime' in this_lane:
               this_lane['complete_datetime']
               # get date in ISO8601 format (YYYY-MM-DD)
               sequenced_date = datetime.strptime( this_lane['complete_datetime'], self.mlwh_datetime_fmt ).strftime( '%Y-%m-%d' )
               num_lanes_sequenced_by_date[sequenced_date] += 1
      return num_lanes_sequenced_by_date
