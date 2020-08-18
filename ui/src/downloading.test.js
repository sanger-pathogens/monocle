import fetchStream from "fetch-readablestream";

import {
  streamDownload,
  streamDownloads,
  downloadsForSample,
} from "./downloading";

jest.mock("streamsaver");
jest.mock("fetch-readablestream");

describe("streamDownload", () => {
  it("calls fetchStream with the given url", async () => {
    // setup
    const filename = "filename.zip";
    const url = "/location";
    const ctrl = jest.mock();
    ctrl.enqueue = jest.fn();
    fetchStream.mockResolvedValue({ body: "some content" });

    // act
    await streamDownload(ctrl, { filename, url });

    // assert
    expect(fetchStream).toHaveBeenCalledWith(url);
  });

  it("calls ctrl.enqueue with the response", async () => {
    // setup
    const filename = "filename.zip";
    const url = "/location";
    const ctrl = jest.mock();
    ctrl.enqueue = jest.fn().mockImplementation((d) => d);
    fetchStream.mockResolvedValue({ body: "some content" });

    // act
    const queued = await streamDownload(ctrl, { filename, url });

    // assert
    expect(ctrl.enqueue).toHaveBeenCalled();
    expect(queued.name).toBe(filename);
    expect(queued.stream()).toBe("some content");
  });
});

describe("streamDownloads", () => {
  it("calls ctrl.enqueue for each", async () => {
    // setup
    const downloads = [
      { filename: "f1", url: "url1" },
      { filename: "f2", url: "url2" },
    ];
    const ctrl = jest.mock();
    ctrl.enqueue = jest.fn().mockImplementation((d) => d);
    fetchStream.mockResolvedValue({ body: "some content" });

    // act
    const queued = await streamDownloads(ctrl, downloads);
    const names = queued.map((d) => d.name);

    // assert
    expect(ctrl.enqueue).toHaveBeenCalledTimes(2);
    expect(names.includes("f1")).toBeTruthy();
    expect(names.includes("f2")).toBeTruthy();
  });
});

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
