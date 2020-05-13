import samplesRaw from "./samples.json";

// samples.json was produced by saving the output
// of `pf info -t study -i 5903` as a tsv, then
// piping through `csv2json -s\t`
export const samples = samplesRaw.map((s) => ({
  laneId: s.lane_id,
  sangerSampleId: s.sample,
  publicName: s.supplier_name,
  submittingInstitution:
    s.lane_id.split("_")[0] === "31663"
      ? "National Reference Laboratories"
      : "The Chinese University of Hong Kong",
  country: s.lane_id.split("_")[0] === "31663" ? "Israel" : "China",
}));

export const institutions = [
  {
    name: "National Reference Laboratories",
    country: "Israel",
  },
  {
    name: "The Chinese University of Hong Kong",
    country: "China",
  },
];
