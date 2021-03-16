import logging
import DataSources.monocledb
import DataSources.sequencing_status
import DataSources.pipeline_status

class MonocleData:
   """
   provides wrapper for classes that query various data sources for Monocle data
   """
   sample_table_inst_key   = 'submitting_institution_id'
   # these are trhe sequencing QC flags from MLWH that are checked; if any are false the sample is counted as failed
   # keys are the keys from the JSON the API giuves us;  strings are what we display on the dashboard when the failure occurs.
   sequencing_flags        = {'qc_lib':   'library',
                              'qc_seq':   'sequencing',
                              }
  
   def __init__(self):
      self.monocledb          = DataSources.monocledb.MonocleDB()
      self.sequencing_status  = DataSources.sequencing_status.SequencingStatus()
      self.pipeline_status    = DataSources.pipeline_status.PipelineStatus()
      # db keys are full institution names strings, but that dashboard wants keys
      # that are alphanumeric only and useable as HTML id attributes; and it is useful to
      # keep data in dicts with keys that match HTML id attr values.
      # these 2 dicts allow mapping between db keys and dict keys, in either direction
      self.institution_dict_to_db_key  = {}
      self.institution_db_key_to_dict  = {}

   def get_progress(self):
      return self.mock_progress

   def get_institutions(self, pattern=None):
      """
      Returns a dict of institutions.
      If option pattern is passed, only institutions with names that include the pattern are returned (case insensitive)
      Dict keys are alphanumeric-only and safe for HTML id attr (do not confuse with database keys).
      MonocleData.institution_dict_to_db_key  and MonocleData.institution_db_key_to_dict (both populated by this method)
      maps internal dict keys to/from the database keys
      """
      names = self.monocledb.get_institution_names()
      institutions = {}
      for this_name in names:
         if None == pattern or pattern.lower() in this_name.lower():
            dict_key = self.institution_name_to_dict_key(this_name, institutions.keys())
            institutions[dict_key] = this_name
            # currently the db uses insitution names as keys, but we don't want to rely on that
            # so store db keys in a pair of hashes to allo lookup both ways
            institution_db_key = this_name
            self.institution_dict_to_db_key[dict_key]             = institution_db_key
            self.institution_db_key_to_dict[institution_db_key]   = dict_key
      return institutions

   def get_samples(self, institutions):
      """
      Pass dict of institutions. Returns a dict of all samples for each institution in the dict.
      """
      unsorted_samples = self.monocledb.get_samples( institutions = list(self.institution_dict_to_db_key.values()) )
      # samples dict keys are same as institutions hash; values are listed (to be filled with samples)
      samples = { i:[] for i in institutions.keys() }
      for this_sample in unsorted_samples:
         this_institution_key = self.institution_db_key_to_dict[ this_sample[self.sample_table_inst_key] ]
         this_sample.pop(self.sample_table_inst_key, None)
         samples[this_institution_key].append( this_sample )
      return samples

   def get_batches(self, institutions):
      """
      Pass dict of institutions. Returns dict with details of batches delivered.
      
      TO DO:  we need to know the total number of samples expected, and ideally batch information
      """
      from datetime  import date
      samples = self.get_samples(institutions)
      batches = { i:{} for i in institutions.keys() }
      for this_institution in institutions.keys():
         num_samples = len(samples[this_institution])
         batches[this_institution] = { 'expected'  : num_samples,
                                       'received'  : num_samples,
                                       'deliveries': [{  'name'   : 'All samples received',
                                                         'date'   : date.today().strftime("%B %d, %Y"),
                                                         'number' : num_samples },
                                                      ]
                                       }
      return batches
      
   def get_sequencing_status(self, institutions, samples):
      """
      Pass dict of institutions and list of samples.
      Returns dict with sequencing status for each institution in the dict.
      
      TO DO:  failures are LANES not SAMPLES;  there could be more lanes than samples
              so in theory we could have more failures than samples.  This is OK
              but in the dashboard code success is calculated as samples - faulures
              and could be a negative number (or at least, misleading)
      TO DO:  improve 'failed' dict 'issue' strings
      """
      status = {}
      for this_institution in institutions.keys():
         status[this_institution] = {  'received'  : len(samples[this_institution]),
                                       'completed' : 0,
                                       'failed'    : [],
                                       }
         sample_id_list = [ s['sample_id'] for s in samples[this_institution] ]
         if 0 < len(sample_id_list):
            sequencing_status_data = self.sequencing_status.get_multiple_samples(sample_id_list)
            for this_sample in samples[this_institution]:
               this_sample_id = this_sample['sample_id']
               # ignore any samples that have no Sanger sample ID
               if this_sample_id is None:
                  logging.warning("a sample from {} has no Sanger sample ID: skipped in sequencing status".format(this_sample_id,institutions[this_institution]))
               # also ignore samples not in the MLWH
               elif this_sample_id not in sequencing_status_data:
                  logging.warning("sample {} ({}) was not found in MLWH: skipped in sequencing status".format(this_sample_id,institutions[this_institution]))
               else:
                  status[this_institution]['completed'] += 1
                  this_sequencing_status = sequencing_status_data[this_sample_id]
                  detected_failure = False
                  for this_lane in this_sequencing_status['lanes']:
                     for this_flag in self.sequencing_flags.keys():
                        if not 1 == this_lane[this_flag]:
                           detected_failure = True
                           status[this_institution]['failed'].append({  'sample' : this_sample_id,
                                                                        'qc'     : self.sequencing_flags[this_flag],
                                                                        'issue'  : "lane {} failed".format(this_lane),
                                                                        },
                                                                     )
                  
      return status
   
   def get_pipeline_status(self, institutions, samples):
      """
      Pass dict of institutions and list of samples; returns dict with pipeline status for each institution in the dict.
      TO DO:  the count here is of LANES rather than SAMPLES, so the dashboard could end up displaying
              more pipeline status results than sequencing status results.   That'snot incorrect but
              the dashboard display needs to be sorted out to make it clear.
      TO DO:  decide what to do about about 'failed' dict 'issue' strings
      """
      status = {}
      for this_institution in sorted( institutions.keys(), key=institutions.__getitem__ ):
         status[this_institution] = {  'sequenced' : 0,
                                       'running'   : 0,
                                       'completed' : 0,
                                       'failed'    : [],
                                       }
         sample_id_list = [ s['sample_id'] for s in samples[this_institution] ]
         if 0 < len(sample_id_list):
            sequencing_status_data = self.sequencing_status.get_multiple_samples(sample_id_list)
         for this_sample_id in sample_id_list:
            if this_sample_id not in sequencing_status_data:
               logging.warning("{} sample {} has no lanes".format(this_institution, this_sample_id))
            else:
               this_sample_lanes = sequencing_status_data[this_sample_id]['lanes']
               for this_lane_id in [ lane['id'] for lane in sequencing_status_data[this_sample_id]['lanes'] ]:
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
