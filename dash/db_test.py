import logging
import pprint
import DataSources.monocledb
import DataSources.sequencing_status
import DataSources.pipeline_status
import DataSources.user_data

logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='INFO')

pp = pprint.PrettyPrinter(indent=3)

#monocledb = DataSources.monocledb.MonocleDB()
#print("Tables:\n")
#for table in monocledb.connection().execute('show tables'):
   #table_name = table[0]
   #print("\n{}".format(table_name))
   #for desc in monocledb.connection().execute('describe {}'.format(table_name)):
      #print("   {}".format(desc))
      
      
#print("\nInstitution names:\n")
#inst_list = monocledb.get_institution_names()
#pp.pprint( inst_list )

#print("\nSamples:\n")
#samples = monocledb.get_samples()
#print("First 3 samples:")
#pp.pprint( samples[0:3] )


#sequencing_status = DataSources.sequencing_status.SequencingStatus()
#print("\nSequencing status:\n")
#test_set = samples[0:3]
#sample_id_list = [ s['sample_id'] for s in test_set ]
#sequencing_status_data = sequencing_status.get_multiple_samples(sample_id_list)
##pp.pprint( sequencing_status_data )
#for this_sample in test_set:
   #this_sample['lane_id'] = [ lane['id'] for lane in sequencing_status_data[this_sample['sample_id']]['lanes'] ]
   #this_sample['sequencing_status'] = sequencing_status_data[this_sample['sample_id']]
#pp.pprint( test_set )


#pipeline_status = DataSources.pipeline_status.PipelineStatus()
#print("\nPipeline status:\n")
#for this_sample in test_set:
   #this_sample['pipeline_status'] = {}
   #logging.debug("getting pipeline status for sample {}".format(this_sample['sample_id']))
   #for this_lane_id in this_sample['lane_id']:
      #if this_lane_id is not None:
         #logging.debug("  lane id = {}".format(this_lane_id))
         #this_sample['pipeline_status'][this_lane_id] = pipeline_status.lane_status(this_lane_id)
      #else:
         #logging.debug("  no lane id: skipping")
#pp.pprint( test_set )

user_data = DataSources.user_data.UserData()
ldap_conn = user_data.connection()

for user in ['ts24','ts24.2','ts24.3']:
   user_stuff  = user_data.username_search(user)
   pp.pprint( "{}".format(user) )
   pp.pprint( "   user data: {}".format(user_stuff) )
   gid = user_stuff[1]['gidNumber'][0].decode('UTF-8')
   #pp.pprint( "   gid: {}".format(gid) )
   group_stuff = user_data.gid_search(gid)
   pp.pprint( "   group data: {}".format(group_stuff) )
