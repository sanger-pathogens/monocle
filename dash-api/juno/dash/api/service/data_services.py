from   collections            import defaultdict
from   csv                    import QUOTE_NONE, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_ALL
from   datetime               import datetime
from   dateutil.relativedelta import relativedelta
import errno
from functools                import reduce
from glob                     import glob
import logging
import os
from   os                     import environ, path
import pandas
from   pathlib                import Path, PurePath
import urllib.parse
from uuid                     import uuid4
import yaml
import urllib.request
import urllib.error

import DataSources.sample_metadata
import DataSources.metadata_download
import DataSources.sequencing_status
import DataSources.pipeline_status
import DataSources.user_data
from utils.file               import format_file_size

ANY_DIR = '*'
API_ERROR_KEY = '_ERROR'
CURRENT_DIR = '.'
DATA_INST_VIEW_ENVIRON  = 'DATA_INSTITUTION_VIEW'
FORMAT_DATE = '%Y-%m-%d' # # YYYY-MM-DD is the date format of ISO 8601
# format of timestamp returned in MLWH queries
FORMAT_MLWH_DATETIME = f'{FORMAT_DATE}T%H:%M:%S%z'
READ_MODE = 'r'
#FIXME: estimate the factor from a wider range of real-world files.
ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS = 3.6

ASSEMBLY_FILE_SUFFIX = '.contigs_spades.fa'
ANNOTATION_FILE_SUFFIX = '.spades.gff'
READS_FILE_SUFFIXES = ('_1.fastq.gz', '_2.fastq.gz')

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

class DataSourceConfigError(Exception):
    pass

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
  
   # date from which progress is counted
   day_zero = datetime(2019,9,17)

   def __init__(self, set_up=True):
      self.user_record                 = None
      self.institutions_data           = None
      self.institution_names           = None
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
         self.data_source_config_name     = 'data_sources.yml'

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
      
      ***IMPORTANT / FIXME***
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

      names = self.get_institution_names()
      institutions = {}
      for this_name in names:
         dict_key = self.institution_name_to_dict_key(this_name, institutions.keys())
         this_db_key = this_name
         institutions[dict_key] = { 'name'   : this_name,
                                    'db_key' : this_db_key
                                  }
         # this allows lookup of the institution dict key from a db key
         self.institution_db_key_to_dict[this_db_key] = dict_key

      self.institutions_data = institutions
      return self.institutions_data

   def get_institution_names(self):
      """
      Return a list of institution names.
      If `user_record` is defined, returns only those institutions that the user is a member of.
      """
      if self.institution_names is not None:
         return self.institution_names

      institution_names = None
      if self.user_record is not None:
         institution_names = [inst['inst_name'] for inst in self.user_record.get('memberOf', [])]
      else:
         institution_names = self.sample_metadata.get_institution_names()

      self.institution_names = institution_names
      return institution_names

   def get_samples(self):
      """
      Returns a dict of all samples for each institution in the dict.
      
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
      Returns dict with sequencing data for each institution the user is a member of; data are in
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
         if len(sample_id_list)-1 > 0: # sample_id_list must be -1 to discount _ERROR entry
            logging.debug("{}.get_sequencing_status() requesting sequencing status for samples {}".format(__class__.__name__,sample_id_list))
            try:
               sequencing_status[this_institution] = self.sequencing_status_source.get_multiple_samples(sample_id_list)
            except urllib.error.HTTPError:
               logging.error("{}.get_sequencing_status() failed to collect samples {} for unknown reason".format(__class__.__name__,sample_id_list))
               sequencing_status[this_institution][API_ERROR_KEY] = 'Server Error: Records cannot be collected at this time. Please try again later.'
         if API_ERROR_KEY not in sequencing_status[this_institution].keys():
            sequencing_status[this_institution][API_ERROR_KEY] = None
      self.sequencing_status_data = sequencing_status
      return self.sequencing_status_data

   def get_batches(self):
      """
      Returns dict with details of batches delivered.
      
      TODO:  find out a way to get the genuine total number of expected samples for each institution
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
         if sequencing_status_data[this_institution][API_ERROR_KEY] is not None:
            batches[this_institution] = { API_ERROR_KEY: 'Server Error: Records cannot be collected at this time. Please try again later.' }
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
         batches[this_institution] = { API_ERROR_KEY: None,
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

      TODO:  improve 'failed' dict 'issue' strings
      """
      institutions_data = self.get_institutions()
      sequencing_status_data = self.get_sequencing_status()
      status = {}
      for this_institution in sequencing_status_data.keys():
         logging.debug("{}.sequencing_status_summary() received sample key pairs {} for institution {}".format(
            __class__.__name__,sequencing_status_data[this_institution].keys(), this_institution))
         if sequencing_status_data[this_institution][API_ERROR_KEY] is not None:
            status[this_institution] = { API_ERROR_KEY: 'Server Error: Records cannot be collected at this time. Please try again later.' }
            continue
         sample_id_list = sequencing_status_data[this_institution].keys()
         status[this_institution] = {  API_ERROR_KEY: None,
                                       'received'  : len(sample_id_list)-1,
                                       'completed' : 0,
                                       'success'   : 0,
                                       'failed'    : 0,
                                       'fail_messages' : [],
                                       }
         if len(sample_id_list)-1 > 0: # sample_id_list must be -1 to discount _ERROR entry
            this_sequencing_status_data = sequencing_status_data[this_institution]
            for this_sample_id in sample_id_list:
               if this_sample_id == API_ERROR_KEY:
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
         
      TODO:  decide what to do about about 'failed' dict 'issue' strings
      """
      institutions_data = self.get_institutions()
      sequencing_status_data = self.get_sequencing_status()
      status = {}
      for this_institution in institutions_data.keys():
         if sequencing_status_data[this_institution][API_ERROR_KEY] is not None:
            status[this_institution] = { API_ERROR_KEY: 'Server Error: Records cannot be collected at this time. Please try again later.' }
            continue
         status[this_institution] = {  API_ERROR_KEY: None,
                                       'running'   : 0,
                                       'completed' : 0,
                                       'success'   : 0,
                                       'failed'    : 0,
                                       'fail_messages' : [],
                                       }
         sample_id_list = sequencing_status_data[this_institution].keys()
         for this_sample_id in sample_id_list:
            if this_sample_id == API_ERROR_KEY:
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

   def get_bulk_download_info(self, inst_key_batch_date_pairs, **kwargs):
      """
      Pass a list of [institution key, batch date] pairs and an optional boolean flag per
      assembly, annotation, and reads types of lane files.
      Returns a dict w/ a summary for an expected sample bulk download.

      {
         num_samples: <int>,
         size: <str>,
         size_zipped: <str>
      }
      """
      samples_from_requested_batches = self.get_samples_from_batches(inst_key_batch_date_pairs)
      public_name_to_lane_files = self.get_public_name_to_lane_files_dict(
         samples_from_requested_batches,
         assemblies=kwargs.get('assemblies', False),
         annotations=kwargs.get('annotations', False),
         reads=kwargs.get('reads', False))
      total_lane_files_size = 0
      for lane_files in public_name_to_lane_files.values():
         lane_files_size = reduce(
            lambda accum, fl: accum + self._get_file_size(fl),
            lane_files,
            0)
         total_lane_files_size = total_lane_files_size + lane_files_size

      return {
         'num_samples': len(samples_from_requested_batches),
         'size': format_file_size(total_lane_files_size),
         'size_zipped': format_file_size(total_lane_files_size / ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS)
      }

   def get_samples_from_batches(self, inst_key_batch_date_pairs):
      """
      Pass a list of [institution key, batch date] pairs.
      Returns a list of samples from the batches.
      """
      if len(inst_key_batch_date_pairs) == 0:
         logging.debug(
            f'{__class__.__name__}.get_samples_from_batches(): The list of [institution key, batch date] pairs is empty.')
         return []

      batch_samples = []
      sequencing_status_data = self.get_sequencing_status()
      for this_inst_key_batch_date_pair in inst_key_batch_date_pairs:
         inst_key         = this_inst_key_batch_date_pair['institution key']
         batch_date_stamp = this_inst_key_batch_date_pair['batch date']
         try:
            samples = [sample for sample in sequencing_status_data[inst_key].values() if sample]
         except KeyError:
            logging.warning(f'No key "{inst_key}" in sequencing status data.')
            continue
         for sample in samples:
            if self.convert_mlwh_datetime_stamp_to_date_stamp(sample['creation_datetime']) == batch_date_stamp:
               batch_samples.append(sample)
      logging.info("batch from {} on {}:  found {} samples".format(inst_key,batch_date_stamp,len(batch_samples)))

      return batch_samples

   def get_public_name_to_lane_files_dict(self, samples, **kwargs):
      """
      Pass a list of samples and an optional boolean flag per assembly, annotation, and reads types of lane files.
      Returns a dict of public names to lane files corresponding to the parameters.

      {
         <public name 1>: [<lane files>],
         <public name 2>: ...
      }
      """
      try:
         data_inst_view_path = environ[DATA_INST_VIEW_ENVIRON]
      except KeyError:
         self._download_config_error(f'environment variable {DATA_INST_VIEW_ENVIRON} is not set')

      public_name_to_lane_files = {}
      assemblies = kwargs.get('assemblies', False)
      annotations = kwargs.get('annotations', False)
      reads = kwargs.get('reads', False)
      data_source_config = self._load_data_source_config()
      try:
         cross_institution_dir = data_source_config['data_download']['cross_institution_dir']
      except KeyError as err:
          self._download_config_error(err)

      data_inst_view_dir = PurePath(data_inst_view_path).name
      for sample in samples:
         if not sample:
            continue
         for lane in sample['lanes']:
            lane_id = lane['id']
            lane_file_names = self._get_lane_file_names(
               lane_id,
               assemblies=assemblies,
               annotations=annotations,
               reads=reads)
            for lane_file_name in lane_file_names:
               lane_file = None
               for file_path in glob(
                  path.join(CURRENT_DIR, data_inst_view_dir, ANY_DIR, lane_file_name)
               ):
                  file = Path(file_path)
                  # Check that the file isn't in the "cross-institution" dir.
                  if cross_institution_dir not in file.parts:
                     lane_file = file
                     break
               else:
                  logging.debug(f'File {lane_file_name} doesn\'t exist')
                  continue
               dir_name = lane_file.resolve().parent.name
               if dir_name not in public_name_to_lane_files:
                  public_name_to_lane_files[dir_name] = []
               public_name_to_lane_files[dir_name].append(lane_file)

      return public_name_to_lane_files

   def _get_lane_file_names(self, lane_id, **kwargs):
      lane_file_names = []
      if kwargs.get('assemblies'):
         lane_file_names.append(f'{lane_id}{ASSEMBLY_FILE_SUFFIX}')
      if kwargs.get('annotations'):
         lane_file_names.append(f'{lane_id}{ANNOTATION_FILE_SUFFIX}')
      if kwargs.get('reads'):
         for file_suffix in READS_FILE_SUFFIXES:
            lane_file_names.append(f'{lane_id}{file_suffix}')
      return lane_file_names

   def get_zip_download_location(self):
      data_source_config      = self._load_data_source_config()
      if DATA_INST_VIEW_ENVIRON not in environ:
         return self._download_config_error("environment variable {} is not set".format(DATA_INST_VIEW_ENVIRON))
      try:
          cross_institution_dir = data_source_config['data_download']['cross_institution_dir']
          return Path(environ[DATA_INST_VIEW_ENVIRON], cross_institution_dir)
      except KeyError as err:
          self._download_config_error(err)

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

   def metadata_as_csv(self, institution, category, status, download_base_url):
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
         
      # get list of samples for this combo of institution/category/status
      # note that the status can only be found by *lane* ID, so we need to look up lanes that match the requirements
      # then the sample ID associated with eacj matchuing lane gets pushed onto a list that we can use for the metadata download request
      samples_for_download = {}
      for this_sample_id in sequencing_status_data[institution_data_key].keys():
         if this_sample_id == API_ERROR_KEY:
            if sequencing_status_data[institution_data_key][
               this_sample_id] == 'Server Error: Records cannot be collected at this time. Please try again later.':
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
                  if this_sample_id in samples_for_download:
                     samples_for_download[this_sample_id].append(this_lane['id'])
                  else:
                     samples_for_download[this_sample_id] = [this_lane['id']]
      logging.info("Found {} samples from {} with {} status {}".format(len(samples_for_download.keys()),institution,category,status))

      # retrieve the sample metadata and load into DataFrame
      logging.info("Requesting metadata for samples: {}".format(samples_for_download))
      metadata,metadata_col_order   = self._metadata_download_to_pandas_data(self.metadata_source.get_metadata(list(samples_for_download.keys())))
      metadata_df                   = pandas.DataFrame(metadata)
      
      # IMPORTANT
      # the metadata returned from the metadata API will (probably) contain lane IDs, for historical reasons:  THESE MUST BE IGNORED
      # instead we use the lane IDs that MLWH told us are associated with each sample, as stored in the samples_for_download dict (just above)
      # it is possible, but rarely (perhaps never in practice) happens, that a smaple may have multiple lane IDs;
      # tin tbhis case they are all put into the lane ID cell
      logging.info("REMINDER: the lane IDs returned by the metadata API are ignored, and the lanes IDs provided by MLWH for each sample are provided in the metadta download!")
      metadata_df = metadata_df.assign( Lane_ID = [ ' '.join(samples_for_download[this_sample_id]) for this_sample_id in metadata_df['Sanger_Sample_ID'].tolist() ] )
      
      # add download links to metadata DataFrame
      metadata_df = metadata_df.assign( Download_Link = [ '/'.join( [download_base_url, urllib.parse.quote(pn)] ) for pn in metadata_df['Public_Name'].tolist() ] )
      logging.info("metadata plus download links DataFrame.head:\n{}".format(metadata_df.head()))   
      
      # if there are any in silico data, these are merged into the metadata DataFrame
      lanes_for_download=[]
      for this_sample in samples_for_download.keys():
         lanes_for_download.extend(samples_for_download[this_sample])
      logging.debug("Requesting in silico data for lanes: {}".format(lanes_for_download))
      in_silico_data,in_silico_data_col_order = self._metadata_download_to_pandas_data(self.metadata_source.get_in_silico_data(lanes_for_download))
      if len(in_silico_data) > 0:
         in_silico_data_df = pandas.DataFrame(in_silico_data)
         logging.debug("in silico data DataFrame.head:\n{}".format(in_silico_data_df.head()))
         # merge with left join on LaneID: incl. all metadata rows, only in silico rows where they match a metadta row
         # validate to ensure lane ID is unique in both dataframes
         metadata_df = metadata_df.merge(in_silico_data_df, left_on='Lane_ID', right_on='Sample_id', how='left', validate="one_to_one")
         del in_silico_data_df
         # add silico data columns to the list
         metadata_col_order = metadata_col_order + in_silico_data_col_order
         
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
   
   def make_download_symlink(self, target_institution=None, **kwargs):
      """
      Pass the institution name _or_ cross_institution=True
      
      This creates a symlink from the web server download directory to the
      directory in which an institution's sample data (annotations,
      assemblies, reads etc.) or a cross-institution sample ZIP file can be found.
      
      The symlink has a random name so only someone given the URL will be
      able to access it.
      
      The symlink path (relative to web server document root) is returned.
      """
      if target_institution is None and not kwargs.get('cross_institution'):
         message="must pass either a target_institution name or 'cross_institution=True'"
         logging.error("{} parameter error: {}".format(__class__.__name__,message))
         raise ValueError(message)
      
      download_config_section = 'data_download'
      download_dir_param      = 'web_dir'
      download_url_path_param = 'url_path'
      cross_institution_dir_param = 'cross_institution_dir'
      # get web server directory, and check it exists
      if not Path(self.data_source_config_name).is_file():
         return self._download_config_error("data source config file {} missing".format(self.data_source_config_name))
      # read config, check required params
      data_sources = self._load_data_source_config()
      if download_config_section not in data_sources or download_dir_param not in data_sources[download_config_section]:
         return self._download_config_error("data source config file {} does not provide the required parameter {}.{}".format(self.data_source_config_name,download_config_section,download_dir_param))
      download_web_dir  = Path(data_sources[download_config_section][download_dir_param])
      if download_config_section not in data_sources or download_url_path_param not in data_sources[download_config_section]:
         return self._download_config_error("data source config file {} does not provide the required parameter {}.{}".format(self.data_source_config_name,download_config_section,download_url_path_param))
      download_url_path  = data_sources[download_config_section][download_url_path_param]
      if download_config_section not in data_sources or cross_institution_dir_param not in data_sources[download_config_section]:
         return self._download_config_error("data source config file {} does not provide the required parameter {}.{}".format(self.data_source_config_name,download_config_section,cross_institution_dir_param))
      cross_institution_dir  = data_sources[download_config_section][cross_institution_dir_param]
      if not download_web_dir.is_dir():
         return self._download_config_error("data download web server directory {} does not exist (or not a directory)".format(str(download_web_dir)))
      logging.debug('web server data download dir = {}'.format(str(download_web_dir)))
      # get the "target" directory where the data for the institution is kept, and check it exists
      # (Why an environment variable? Because this can be set by docker-compose, and it is a path
      # to a volume mount that is also set up by docker-compose.)
      if DATA_INST_VIEW_ENVIRON not in environ:
         return self._download_config_error("environment variable {} is not set".format(DATA_INST_VIEW_ENVIRON))
      child_dir = cross_institution_dir if kwargs.get('cross_institution') else self.institution_db_key_to_dict[target_institution]
      download_host_dir = Path(environ[DATA_INST_VIEW_ENVIRON], child_dir)
      if not download_host_dir.is_dir():
         return self._download_config_error("data download host directory {} does not exist (or not a directory)".format(str(download_host_dir)))
      logging.debug('host data download dir = {}'.format(str(download_host_dir)))
      # create a randomly named symlink to present to the user (do..while is just in case the path exists already)
      while True:
         random_name          = uuid4().hex
         data_download_link   = Path(download_web_dir, random_name)
         download_url_path    = '/'.join([download_url_path, random_name])
         if not data_download_link.exists():
            break
      logging.debug('creating symlink {} -> {}'.format(str(data_download_link),str(download_host_dir)))
      data_download_link.symlink_to(download_host_dir.absolute())
      return download_url_path

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
      if sequencing_status_data[institution][API_ERROR_KEY] is not None:
         return {}
      num_samples_received_by_date  = defaultdict(int)
      for this_sample_id in samples_received:
         if this_sample_id == API_ERROR_KEY:
            continue
         received_date = self.convert_mlwh_datetime_stamp_to_date_stamp(
            sequencing_status_data[institution][this_sample_id]['creation_datetime'])
         num_samples_received_by_date[received_date] += 1
      return num_samples_received_by_date
   
   def num_lanes_sequenced_by_date(self, institution):
      sequencing_status_data        = self.get_sequencing_status()
      if sequencing_status_data[institution][API_ERROR_KEY] is not None:
         return {}
      samples_received              = sequencing_status_data[institution].keys()
      num_lanes_sequenced_by_date   = defaultdict(int)

      for this_sample_id in samples_received:
         if this_sample_id == API_ERROR_KEY:
            continue
         # get each lane (some samples may have non lanes yet)
         for this_lane in sequencing_status_data[institution][this_sample_id]['lanes']:
            # get timestamp for completion (some lanes may not have one yet)
            if 'complete_datetime' in this_lane:
               this_lane['complete_datetime']
               sequenced_date = self.convert_mlwh_datetime_stamp_to_date_stamp(
                  this_lane['complete_datetime'])
               num_lanes_sequenced_by_date[sequenced_date] += 1
      return num_lanes_sequenced_by_date

   def convert_mlwh_datetime_stamp_to_date_stamp(self, datetime_stamp):
      return datetime.strptime(datetime_stamp,
         FORMAT_MLWH_DATETIME
      ).strftime( FORMAT_DATE )

   def _get_file_size(self, path_instance):
      try:
         # FIXME delete next 2 lines when done testing
         size=path_instance.stat().st_size
         logging.debug(f'counting size of download file: {path_instance}  {size}')
         return path_instance.stat().st_size
      except OSError as err:
         logging.info(f'Failed to open file {path_instance}: {err}')
         return 0

   def _load_data_source_config(self):
      try:
         with open(self.data_source_config_name, READ_MODE) as data_source_config_file:
            return yaml.load(data_source_config_file, Loader=yaml.FullLoader)
      except EnvironmentError as err:
         self._download_config_error(err)

   def _download_config_error(self, description):
      """
      Call for errors occurring in make_download_symlink().
      Pass error description of problem, which is logged.
      Raises DataSourceConfigError.
      """
      message="Invalid data download config: {}".format(description)
      logging.error(message)
      raise DataSourceConfigError(message)
