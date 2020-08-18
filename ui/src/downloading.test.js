const { isTerminating } = require("apollo-link/lib/linkUtils");

import { downloadsForSample } from "./downloading";

describe("downloadsForSample", () => {
  const laneId = "31663_7#113";

  it("contains four files", () => {
    const downloads = downloadsForSample(laneId);

    expect(downloads.length).toBe(4);
  });

  it("contains paired reads", () => {
    const downloads = downloadsForSample(laneId);

    expect(
      downloads.map((d) => d.filename).filter((d) => d.endsWith("_1.fastq.gz"))
        .length
    ).toBe(1);
    expect(
      downloads.map((d) => d.filename).filter((d) => d.endsWith("_2.fastq.gz"))
        .length
    ).toBe(1);
  });

  it("contains assembly", () => {
    const downloads = downloadsForSample(laneId);

    expect(
      downloads.map((d) => d.filename).filter((d) => d.endsWith(".fa")).length
    ).toBe(1);
  });

  it("contains annotation", () => {
    const downloads = downloadsForSample(laneId);

    expect(
      downloads.map((d) => d.filename).filter((d) => d.endsWith(".gff")).length
    ).toBe(1);
  });
});
