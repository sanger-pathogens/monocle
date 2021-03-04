import pprint
import MonocleDash.monocleclient

data  = MonocleDash.monocleclient.MonocleData()
pp    = pprint.PrettyPrinter(indent=3)

#prog = data.get_progress()
#print("Progress:\n")
#pp.pprint(prog)

inst = data.get_institutions()
print("\nInstitutions:\n")
pp.pprint(inst)

samples = data.get_samples(inst)
print("\nSamples:\n")
pp.pprint(samples)

#batches = data.get_batches(inst)
#print("\nBatches:\n")
#pp.pprint(batches)

#sequencing_status = data.get_sequencing_status(inst)
#print("\nSequencing status:\n")
#pp.pprint(sequencing_status)

#pipeline_status = data.get_pipeline_status(inst)
#print("\nPipeline status:\n")
#pp.pprint(pipeline_status)
