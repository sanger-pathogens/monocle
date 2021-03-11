import logging
import pprint
import DataSources.monocledb
import DataSources.pipeline_status

logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='INFO')

monocledb         = DataSources.monocledb.MonocleDB()
pipeline_status   = DataSources.pipeline_status.PipelineStatus()
pp                = pprint.PrettyPrinter(indent=3)

#print("Tables:\n")
#for table in monocledb.connection().execute('show tables'):
   #table_name = table[0]
   #print("\n{}".format(table_name))
   #for desc in monocledb.connection().execute('describe {}'.format(table_name)):
      #print("   {}".format(desc))
      
#print("\nInstitution names:\n")
#pp.pprint( monocledb.get_institution_names() )

#print("\nSamples:\n")
#inst_list = monocledb.get_institution_names()
#samples = monocledb.get_samples()
#pp.pprint( samples )

print("\nPipeline status:\n")
samples = monocledb.get_samples()
for this_sample in samples:
   logging.debug("getting status for sample {}".format(this_sample['sample_id']))
   this_lane_id = this_sample['lane_id']
   if this_lane_id is not None:
      logging.debug("  lane id = {}".format(this_lane_id))
      this_sample['pipeline_status'] = pipeline_status.lane_status(this_lane_id)
   else:
      logging.debug("  no lane id: skipping")
pp.pprint( samples )
