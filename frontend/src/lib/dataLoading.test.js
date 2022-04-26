import env from "$app/env";
import { PATHNAME_LOGIN } from "$lib/constants.js";
import {
  getBatches,
  getBulkDownloadInfo,
  getBulkDownloadUrls,
  getColumns,
  getDistinctColumnValues,
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
const DATA_TYPE_METADATA = "metadata";

const DISTINCT_COLUMN_VALUES_STATE = {
  metadata: {
    serotype: ["1a", "1b", "NT"],
    country: ["doesn't", " mattter"]
  },
  "in silico": {
    ST: ["doesn't", " mattter"]
  }
};
const FILTER_STATE = {
  metadata: {
    serotype: { values: ["1a", "1b"], exclude: true },
    country: { values: ["AU"] }
  },
  "in silico": { ST: { values: ["x", "y"] } }
};

const fetch = jest.fn();

jest.mock("$app/env", () => ({
  get browser() {
    return true;
  }
}));

describe("if unauthenticated", () => {
  delete global.location;
  global.location = { pathname: "" };

  afterAll(() => document.cookie = "nginxauth=fake-auth-token");

  it("redirects to the login page w/o making a fetch request", async () => {
    const result = await getBatches(fetch);

    expect(fetch).not.toHaveBeenCalled();
    expect(location.href.endsWith(PATHNAME_LOGIN))
      .toBeTruthy();
    expect(result).toStrictEqual({});
  });

  it("doesn't redirect to the login page if it's already the login page", async () => {
    global.location = { pathname: PATHNAME_LOGIN };

    const result = await getBatches(fetch);

    expect(fetch).not.toHaveBeenCalled();
    expect(location.href).toBeUndefined();
    expect(result).toStrictEqual({});
  });

  it("does make a fetch request if the environment isn't \"browser\" w/o redirecting to the login page", async () => {
    const browserSpy = jest.spyOn(env, "browser", "get");
    const expectedPayload = "batches";
    browserSpy.mockReturnValueOnce(false);
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ batches: expectedPayload })
    });

    const actualPayload = await getBatches(fetch);

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(actualPayload).toBe(expectedPayload);
    expect(location.href).toBeUndefined();
  });
});

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
    args: [{
      instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
      filter: { filterState: FILTER_STATE, distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE },
      assemblies: true,
      annotations: false,
      reads: true
    }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "in silico": { ST: ["x", "y"] }
        },
        assemblies: true,
        annotations: false,
        reads: true
      })
    },
    expectedEndpoints: ["bulk_download_info"],
    responsePayload: "as is",
    expectedResult: "as is"
  },
  {
    fnName: "getBulkDownloadUrls",
    getResource: getBulkDownloadUrls,
    args: [{
      instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
      filter: { filterState: FILTER_STATE, distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE },
      assemblies: true,
      annotations: false,
      reads: true
    }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "in silico": { ST: ["x", "y"] }
        },
        assemblies: true,
        annotations: false,
        reads: true
      })
    },
    expectedEndpoints: ["bulk_download_urls"],
    responsePayload: {
      download_urls: ["fake_url"],
    },
    expectedResult: ["fake_url"]
  },
  {
    fnName: "getColumns",
    getResource: getColumns,
    expectedEndpoints: ["get_field_attributes"],
    responsePayload: {
      "field_attributes": "inner response payload",
    },
    expectedResult: "inner response payload"
  },
  {
    fnName: "getDistinctColumnValues",
    getResource: getDistinctColumnValues,
    args: [{
      instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
      columns: [{
        name: "age_group",
        dataType: DATA_TYPE_METADATA
      }, {
        name: "ST",
        dataType: "in silico"
      }, {
        name: "serotype",
        dataType: DATA_TYPE_METADATA
      }],
      filter: { filterState: FILTER_STATE, distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE },
    }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "in silico": { ST: ["x", "y"] }
        },
        fields: [
          { "field type": DATA_TYPE_METADATA, "field names": ["age_group", "serotype"] },
          { "field type": "in silico", "field names": ["ST"] }
        ]
      })
    },
    expectedEndpoints: ["get_distinct_values"],
    responsePayload: {
      "distinct values": "inner response payload",
    },
    expectedResult: "inner response payload"
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
    args: [{
      instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
      filter: { filterState: FILTER_STATE, distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE },
      columns: { metadata: ["some column"], "in silico": ["a column", "another column"] },
      numRows: 14,
      startRow: 2
    }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "in silico": { ST: ["x", "y"] }
        },
        "num rows": 14,
        "start row": 2,
        "metadata columns": ["some column"],
        "in silico columns": ["a column", "another column"]
      })
    },
    expectedEndpoints: ["get_metadata"],
    responsePayload: "as is",
    expectedResult: "as is"
  },
  {
    fnName: "getSampleMetadata",
    getResource: getSampleMetadata,
    args: [{
      instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
      filter: { filterState: FILTER_STATE, distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE },
      numRows: 14,
      startRow: 2,
      asCsv: true
    }],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "in silico": { ST: ["x", "y"] }
        },
        "num rows": 14,
        "start row": 2,
        "as csv": true
      })
    },
    expectedEndpoints: ["get_metadata"],
    responsePayload: "blob",
    expectedResult: "blob"
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
      blob: () => Promise.resolve(responsePayload),
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

  it("resolves 404 Not Found to `undefined`", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404
    });

    await expect(getResource(...args, fetch)).resolves.toBeUndefined();
  });
});
