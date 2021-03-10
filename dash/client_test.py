import pprint
import MonocleDash.monocleclient

data  = MonocleDash.monocleclient.MonocleData(pipeline_status_csv_file='../data/status/pipelines.csv')
pp    = pprint.PrettyPrinter(indent=3)

#print("Progress:\n")
#prog = data.get_progress()
#pp.pprint(prog)

print("\nInstitutions:\n")
inst = data.get_institutions()
pp.pprint(inst)

#print("\nSamples:\n")
#samples = data.get_samples(inst)
#pp.pprint(samples)

#print("\nBatches:\n")
#batches = data.get_batches(inst)
#pp.pprint(batches)

#print("\nSequencing status:\n")
#sequencing_status = data.get_sequencing_status(inst)
#pp.pprint(sequencing_status)

print("\nPipeline status:\n")
samples = data.get_samples(inst)
pipeline_status = data.get_pipeline_status(inst,samples)
pp.pprint(pipeline_status)
