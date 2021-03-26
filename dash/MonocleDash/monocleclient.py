import logging
import DataSources.monocledb
import DataSources.sequencing_status
import DataSources.pipeline_status

class MonocleData:
   """
   Provides wrapper for classes that query various data sources for Monocle data.
   This class exists to convert data between the form in which they are provided by the data sources,
   and whatever form is most convenient for rendering the dashboard.
   """
   sample_table_inst_key   = 'submitting_institution_id'
   # these are trhe sequencing QC flags from MLWH that are checked; if any are false the sample is counted as failed
   # keys are the keys from the JSON the API giuves us;  strings are what we display on the dashboard when the failure occurs.
   sequencing_flags        = {'qc_lib':   'library',
                              'qc_seq':   'sequencing',
                              }
  
   def __init__(self):
      self.monocledb                   = DataSources.monocledb.MonocleDB()
      self.institutions_data           = None
      self.samples_data                = None
      self.sequencing_status_source    = DataSources.sequencing_status.SequencingStatus()
      self.sequencing_status_data      = None
      self.pipeline_status             = DataSources.pipeline_status.PipelineStatus()
      self.institution_db_key_to_dict  = {} # see get_institutions for the purpose of this

   def get_progress(self):
      return self.mock_progress

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
      
      TO DO:  we need to know the total number of samples expected, and ideally batch information
      """
      from datetime  import date
      samples = self.get_samples()
      institutions_data = self.get_institutions()
      batches = { i:{} for i in institutions_data.keys() }
      for this_institution in institutions_data.keys():
         num_samples = len(samples[this_institution])
         batches[this_institution] = { 'expected'  : num_samples,
                                       'received'  : num_samples,
                                       'deliveries': [{  'name'   : 'All samples received',
                                                         'date'   : date.today().strftime("%B %d, %Y"),
                                                         'number' : num_samples },
                                                      ]
                                       }
      return batches
      
   def sequencing_status_summary(self):
      """
      Returns dict with a summary of sequencing outcomes for each institution.
      
      {  institution_1: {  'received':    <int>,
                           'completed':   <int>,
                           'failed':      [  {  'lane':  lane_id_1,
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
                                       'failed'    : [],
                                       }
         if 0 < len(sample_id_list) and this_institution in sequencing_status_data:
            this_sequencing_status_data = sequencing_status_data[this_institution]
            for this_sample_id in sample_id_list:
               # ignore any samples that have no Sanger sample ID
               if this_sample_id is None:
                  logging.warning("a sample from {} has no Sanger sample ID: skipped in sequencing status".format(this_sample_id,institutions_data[this_institution]['name']))
               # also ignore samples not in the MLWH
               elif this_sample_id not in this_sequencing_status_data:
                  logging.warning("sample {} ({}) was not found in MLWH: skipped in sequencing status".format(this_sample_id,institutions_data[this_institution]['name']))
               else:
                  this_sample_lanes = this_sequencing_status_data[this_sample_id]['lanes']
                  if len(this_sample_lanes) > 0:
                     # is a sample is in MLWH but there are no lane data, it means sequencing hasn't been done yet
                     status[this_institution]['completed'] += 1
                     detected_failure = False
                     for this_lane in this_sample_lanes:
                        for this_flag in self.sequencing_flags.keys():
                           if not 1 == this_lane[this_flag]:
                              detected_failure = True
                              status[this_institution]['failed'].append({  'lane'   : "{} (sample {})".format(this_lane['id'], this_sample_id),
                                                                           'stage'  : self.sequencing_flags[this_flag],
                                                                           'issue'  : "lane {} failed".format(this_lane),
                                                                           },
                                                                        )
      return status
   
   def pipeline_status_summary(self):
      """
      Returns dict with summary of the pipeline outcomes for each institution.

      {  institution_1: {  'sequenced':   <int>,
                           'running':     <int>,
                           'completed':   <int>,
                           'failed':      [  {  'lane':  lane_id_1,
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
         status[this_institution] = {  'sequenced' : 0,
                                       'running'   : 0,
                                       'completed' : 0,
                                       'failed'    : [],
                                       }
         sample_id_list = sequencing_status_data[this_institution].keys()
         if 0 < len(sample_id_list):
            for this_sample_id in sample_id_list:
               this_sample_lanes = sequencing_status_data[this_institution][this_sample_id]['lanes']
               for this_lane_id in [ lane['id'] for lane in this_sample_lanes ]:
                  this_pipeline_status = self.pipeline_status.lane_status(this_lane_id)
                  status[this_institution]['sequenced'] += 1
                  if this_pipeline_status['FAILED']:
                     for this_stage in self.pipeline_status.pipeline_stage_fields:
                        if this_pipeline_status[this_stage] == self.pipeline_status.stage_failed_string:
                           status[this_institution]['failed'].append({  'lane'   : "{} (sample {})".format(this_lane_id, this_sample_id),
                                                                        'stage'  : this_stage,
                                                                        # currently have no way to retrieve a failure report
                                                                        'issue'  : 'sorry, failure mesages cannot currently be seen here',
                                                                        },           
                                                                     )
                  else:
                     if this_pipeline_status['COMPLETED']:
                        status[this_institution]['completed'] += 1
                     else:
                        # not completed, but no failures reported
                        status[this_institution]['running'] += 1
      return status

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


   mock_progress = { 'months'             : [1,2,3,4,5,6,7,8,9],
                     'samples received'   : [158,225,367,420,580,690,750,835,954],
                     'samples sequenced'  : [95,185,294,399,503,640,730,804,895],
                     }
