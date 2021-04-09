import logging
import pprint
import MonocleDash.monocleclient

logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='INFO')

data  = MonocleDash.monocleclient.MonocleData()
pp    = pprint.PrettyPrinter(indent=3)

#print("Progress:\n")
#prog = data.get_progress()
#pp.pprint(prog)

print("\nInstitutions:\n")
inst = data.get_institutions()#'hong kong')
#pp.pprint(inst)

print("\nSamples:\n")
data.get_samples()
### add a sample that is missing from monocle db because it wasn't sequenced
### sample ID is genuine, should exist in MLWH
## note data.get_samples() must be called before we insert this, so that
## the data.samples_data list is populated with the real samples
#data.samples_data['TheChiUniHonKon'].append( {  'host_status':  'carriage',
                                                #'lane_id'      : None,
                                                #'public_name'  : 'JN_HK_this_is_never_used_so_does_not_matter',
                                                #'sample_id'    : '5903STDY8059082',
                                                #'serotype'     : 'NT'
                                                #}
                                             #)
samples = data.get_samples()
#pp.pprint(samples)

print("\nProgress:\n")
progress = data.get_progress()
pp.pprint(progress)

#print("\nBatches:\n")
#batches = data.get_batches()
#pp.pprint(batches)

#print("\nSequencing status:\n")
#sequencing_status = data.sequencing_status_summary()
#pp.pprint(sequencing_status)

#print("\nPipeline status:\n")
#pipeline_status = data.pipeline_status_summary()
#pp.pprint(pipeline_status)
