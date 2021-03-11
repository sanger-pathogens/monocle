import configparser
import logging
import yaml
from   sqlalchemy       import create_engine
from   sqlalchemy.sql   import text
from   urllib.parse     import quote as urlencode

class DataSourceParamError(Exception):
   """ exception when data source methods are aclled with invalid parameter(s) """
   pass

class MonocleDB:
   """ provides access to the Monocle database """
   
   data_sources_config        = 'data_sources.yml'
   data_source                = 'monocledb'
   institution_table          = 'api_institution'
   institution_table_inst_key = 'name'
   sample_table               = 'api_sample'
   sample_table_inst_key      = 'submitting_institution_id'
   sample_table_fields        = ['lane_id', 'sample_id', 'public_name', 'host_status', 'serotype', sample_table_inst_key]

   def __init__(self):
      with open(self.data_sources_config, 'r') as file:
         data_sources = yaml.load(file, Loader=yaml.FullLoader)
         db_cnf_file = data_sources[self.data_source]['cnf_file']
         logging.info("Reading database config from {}".format(db_cnf_file))
         db_config = configparser.ConfigParser()
         db_config.read(db_cnf_file)
         db_password = urlencode( db_config['client']['password'].strip('"') )
         self.db_url = "mysql://{}:{}@{}:{}/{}".format(  db_config['client']['user'],
                                                         db_password,
                                                         db_config['client']['host'],
                                                         db_config['client']['port'],
                                                         db_config['client']['database'],
                                                         )
      logging.info("Database URL {}".format( self.db_url.replace(db_password, 'SECRET') ))
      self.db_engine = None

   def connection(self):
      if self.db_engine is None:
         self.db_engine = create_engine( self.db_url, echo = False )
      connection = self.db_engine.connect()
      logging.debug("opened db connection")
      return connection
      
   def get_institution_names(self):
      institutions = None
      with self.connection() as conn:
         #rs = conn.execute(text("""select * from api_institution where country = :the_country"""), the_country='China')
         #rs = conn.execute('describe api_institution')
         results = conn.execute( 'select {} from {}'.format(self.institution_table_inst_key, self.institution_table) )
         institutions = []
         for row in results:
            # TO DO: sanity check row[0] as an institution name
            institutions.append( row[0] )
         logging.info("found {} institutions in monocle db".format(len(institutions)))
      return institutions
   
   def get_samples(self, institutions=None):
      if institutions is not None and not isinstance(institutions, list):
         raise DataSourceParamError( "named parameter 'institutions' is {}, should be a list".format(type(institutions)) )
      with self.connection() as conn:
         sql = "select * from {}".format(self.sample_table)
         if institutions is not None:
            sql += ' where {} in ("{}")'.format(self.sample_table_inst_key, '","'.join(institutions))
         results = conn.execute( sql )
         samples = []
         for row in results:
            this_sample = {}
            r = 0
            for this_field in self.sample_table_fields:
               this_sample[this_field] = row[r]
               r += 1
            samples.append( this_sample )
         logging.info("found {} samples in monocle db".format(len(samples)))
      return samples
      
