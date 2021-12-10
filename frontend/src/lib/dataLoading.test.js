import {
  getBatches,
  getBulkDownloadInfo,
  getBulkDownloadUrls,
  getInstitutionStatus,
  getProjectProgress,
  getSampleMetadata,
  getUserDetails
} from "./dataLoading.js";

const INST_KEY_BATCH_DATE_PAIRS = [
  ["SomIns", "2021-05-20"],
  ["AnoIns", "2020-09-01"]
];
const INST_KEY_BATCH_DATE_OBJECTS = INST_KEY_BATCH_DATE_PAIRS.map(([instKey, batchDate]) => (
  { "institution key": instKey, "batch date": batchDate }
));
const DASHBOARD_API_URL = "/dashboard-api";

const fetch = jest.fn();

describe.each([
  {
    fnName: "getBatches",
    getResource: getBatches,
    expectedEndpoints: ["get_batches"],
    responsePayload: {
      batches: {
        some: "data",
      }
    },
    expectedResult: { some: "data" }
  },
  {
    fnName: "getBulkDownloadInfo",
    getResource: getBulkDownloadInfo,
    args: [INST_KEY_BATCH_DATE_PAIRS, { assemblies: true, annotations: false }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": { batches: INST_KEY_BATCH_DATE_OBJECTS },
        assemblies: true,
        annotations: false
      })
    },
    expectedEndpoints: ["bulk_download_info"],
    responsePayload: "as is",
    expectedResult: "as is"
  },
  {
    fnName: "getBulkDownloadUrls",
    getResource: getBulkDownloadUrls,
    args: [INST_KEY_BATCH_DATE_PAIRS, { assemblies: true, annotations: false }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": { batches: INST_KEY_BATCH_DATE_OBJECTS },
        assemblies: true,
        annotations: false
      })
    },
    expectedEndpoints: ["bulk_download_urls"],
    responsePayload: {
      download_urls: ["fake_url"],
    },
    expectedResult: ["fake_url"]
  },
  {
    fnName: "getInstitutionStatus",
    getResource: getInstitutionStatus,
    expectedEndpoints: ["get_institutions", "get_batches", "sequencing_status_summary", "pipeline_status_summary"],
    responsePayload: {
      institutions: {
        CRS: { name: "Center for Reducing Suffering" },
        SR: { name: "Sentience Research" }
      },
      batches: {},
      sequencing_status: {
        CRS: { success: 42 },
        SR: { success: 99 }
      },
      pipeline_status: {}
    },
    expectedResult: [{
      batches: undefined,
      key: "CRS",
      name: "Center for Reducing Suffering",
      pipelineStatus: { sequencedSuccess: 42 },
      sequencingStatus: { success: 42 }
    }, {
      batches: undefined,
      key: "SR",
      name: "Sentience Research",
      pipelineStatus: { sequencedSuccess: 99 },
      sequencingStatus: { success: 99 }
    }]
  },
  {
    fnName: "getProjectProgress",
    getResource: getProjectProgress,
    expectedEndpoints: ["get_progress"],
    responsePayload: {
      progress_graph: {
        data: { date: "21.08.21", "samples received": 200, "samples sequenced": 50 },
      }
    },
    expectedResult: {
      datasets: [
        { name: "received", values: 200 },
        { name: "sequenced", values: 50}
      ],
      dates: "21.08.21"
    }
  },
  {
    fnName: "getSampleMetadata",
    getResource: getSampleMetadata,
    args: [{ instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS, numRows: 14, startRow: 2 }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": { batches: INST_KEY_BATCH_DATE_OBJECTS },
        "num rows": 14,
        "start row": 2
      })
    },
    expectedEndpoints: ["get_metadata"],
    responsePayload: "as is",
    expectedResult: "as is"
  },
  {
    fnName: "getUserDetails",
    getResource: getUserDetails,
    expectedEndpoints: ["get_user_details"],
    responsePayload: {
      user_details: {
        type: "support"
      }
    },
    expectedResult: {
      type: "support"
    }
  }
])("$fnName", ({
  getResource, args = [], expectedEndpoints, expectedFetchOpts, responsePayload, expectedResult
}) => {
  beforeEach(() => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(responsePayload)
    });
  });

  it("fetches the data from the correct endpoints", async () => {
    fetch.mockClear();

    await getResource(...args, fetch);

    expect(fetch).toHaveBeenCalledTimes(expectedEndpoints.length);
    expectedEndpoints.forEach((expectedEndpoint, i) => {
      const fetchArgs = fetch.mock.calls[i];
      expect(fetchArgs[0]).toBe(`${DASHBOARD_API_URL}/${expectedEndpoint}`);
      const actualFetchOpts = fetchArgs[1];
      expect([undefined, expectedFetchOpts]).toContainEqual(actualFetchOpts);
    });
  });

  it("returns result in the correct format", async () => {
    const result = await getResource(...args, fetch);

    expect(result).toEqual(expectedResult);
  });
});
