import pprint
import DataSources.monocledb
import DataSources.pipeline_status

monocledb         = DataSources.monocledb.MonocleDB()
pipeline_status   = DataSources.pipeline_status.PipelineStatus(csv_file='../data/status/pipelines_test.csv')
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
   if this_sample['lane_id'] is not None:
      this_sample['pipeline_status'] = pipeline_status.lane_status(this_sample['lane_id'])
pp.pprint( samples )
