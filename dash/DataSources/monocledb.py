import configparser
import logging
import sqlalchemy
import yaml
from   urllib.parse  import quote as urlencode

import datetime

class DataSourceParamError(Exception):
   """ exception when data source methods are aclled with invalid parameter(s) """
   pass

class MonocleDB:
   """
   Methods for retrieving data from the the Monocle database.
   """
   
   data_sources_config        = 'data_sources.yml'
   data_source                = 'monocledb'
   data_source_cnf_file_param = 'cnf_file'
   required_config_params     = [   data_source_cnf_file_param,
                                    'institution_table',
                                    'institution_table_inst_key',
                                    'sample_table',
                                    'sample_table_inst_key',
                                    'sample_table_lane_id_field',
                                    'sample_table_fields',
                                    ]
   required_db_params         = [   'user',
                                    'password',
                                    'host',
                                    'port',
                                    'database'
                                    ]

   def __init__(self, set_up=True):
      """
      Constructor.  Reads config from default config file by default;
      pass set_up=False to prevent config being dong on instaiation, and
      subsequently you can call set_up() to configure with a config file of your choice
      """
      self.db_engine = None
      self.db_url    = None
      if set_up:
         self.set_up(self.data_sources_config)
         logging.info("read monocle db config: {}".format(self.config))

   def set_up(self, config_file_name):
      """
      read config from named file
      """
      with open(config_file_name, 'r') as file:
         data_sources = yaml.load(file, Loader=yaml.FullLoader)
         self.config = data_sources[self.data_source]
         for required_param in self.required_config_params:
            if not required_param in self.config:
               logging.error("data source config file {} does not provide the required paramter {}.{}".format(self.data_sources_config,self.data_source,required_param))
               raise KeyError
         # database connection config is in a separate .cnf file
         self.read_db_config(self.config[self.data_source_cnf_file_param])

   def read_db_config(self, cnf_file):
      """
      read db config from named file
      the default file will have been read if set_up() was called, but it can be called separately
      if you want to load db credentials from a different .cnf file
      """
      logging.info("Reading database config from {}".format(cnf_file))
      # configparser.ConfigParser doesn't raise appropriate exception if the file doesn't exist, so...
      open(cnf_file).close()
      db_config = configparser.ConfigParser()
      db_config.read(cnf_file)
      for required_param in self.required_db_params:
         if not required_param in db_config['client']:
            logging.error("database .cnf file {} does not provide the required paramter client.{}".format(cnf_file,required_param))
            raise KeyError
      enc_password = urlencode( db_config['client']['password'].strip('"') )
      url = "mysql://{}:{}@{}:{}/{}".format( db_config['client']['user'],
                                             enc_password,
                                             db_config['client']['host'],
                                             db_config['client']['port'],
                                             db_config['client']['database'],
                                             )
      self.db_url = url
      logging.info("Database URL {}".format( self.db_url.replace(enc_password, 'SECRET') ))
      return self.db_url

   def make_query(self, sql):
      """
      Connects to db and executes the SQL query passed.
      Returns iterable sqlalchemy.engine.result.ResultProxy object
      """
      if self.db_engine is None:
         self.db_engine = sqlalchemy.create_engine( self.db_url, echo = False )
      with self.db_engine.connect() as conn:
         logging.debug("opened db connection")
         results = conn.execute( sql )
         return results

   def get_institution_names(self):
      """
      Returns a list of all instiution names
      """
      institutions = []
      results = self.make_query( 'select {} from {}'.format(self.config['institution_table_inst_key'], self.config['institution_table']) )
      for row in results:
         # TO DO: sanity check row[0] as an institution name
         institutions.append( row[0] )
      logging.info("found {} institutions in monocle db".format(len(institutions)))
      return institutions

   def get_samples(self, exclude_lane_id=True, institutions=None):
      """
      Retrieve all sample records; return as array of dicts, dict keys are field names from monocle db
      Optional params:
      `exclude_lane_id`, flag; if true, `lane_id` is excluded from the dicts returned
      `institutions`, a list of institution names; only samples from those listed are returned
      """
      if institutions is not None and not isinstance(institutions, list):
         raise DataSourceParamError( "named parameter 'institutions' is {}, should be a list".format(type(institutions)) )
      sql = "select * from {}".format(self.config['sample_table'])
      if institutions is not None:
         sql += ' where {} in ("{}")'.format(self.config['sample_table_inst_key'], '","'.join(institutions))
      results = self.make_query(sql)
      samples = []
      for row in results:
         this_sample = {}
         r = 0
         for this_field in self.config['sample_table_fields']:
            if exclude_lane_id and this_field == self.config['sample_table_lane_id_field']:
               logging.debug("excluding the {} table field {} from the sample data".format(self.config['sample_table'],this_field))
            else:
               this_sample[this_field] = row[r]
               if None == this_sample[this_field]:
                  logging.warn("monocle db: record in {} has null {}: {}".format(self.config['sample_table'],this_field,row))
            r += 1
         samples.append( this_sample )
      logging.info("found {} samples in monocle db".format(len(samples)))
      return samples
      
