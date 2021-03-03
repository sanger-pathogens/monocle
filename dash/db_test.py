import pprint
import DataSources.monocledb

monocledb   = DataSources.monocledb.MonocleDB()
pp          = pprint.PrettyPrinter(indent=3)

#print("Tables:\n")
#for table in monocledb.connection().execute('show tables'):
   #table_name = table[0]
   #print("\n{}".format(table_name))
   #for desc in monocledb.connection().execute('describe {}'.format(table_name)):
      #print("   {}".format(desc))
      
#print("\nInstitution names:\n")
#pp.pprint( monocledb.get_institution_names() )

print("\nSamples:\n")
inst_list = monocledb.get_institution_names()
samples = monocledb.get_samples()
pp.pprint( samples )
