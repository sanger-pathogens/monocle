import logging
import yaml
from   sqlalchemy       import create_engine
from   sqlalchemy.sql   import text



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
      these_credentials = data_sources[self.data_source]
      self.db_url = "mysql://{}:{}@{}:{}/{}".format(  these_credentials['user'],
                                                      these_credentials['password'],
                                                      these_credentials['host'],
                                                      these_credentials['port'],
                                                      these_credentials['database'],
                                                      )
      self.db_engine       = None

   def connection(self):
      if self.db_engine is None:
         self.db_engine = create_engine( self.db_url, echo = False )
      connection = self.db_engine.connect()
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
      return institutions
   
   def get_samples(self, institutions=None):
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
      return samples
      
