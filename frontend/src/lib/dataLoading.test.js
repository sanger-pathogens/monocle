import environment from "$app/environment";
import {
  HTTP_HEADER_CONTENT_TYPE,
  HTTP_HEADERS_JSON,
  HTTP_STATUS_CODE_UNAUTHORIZED,
  MIME_TYPE_HTML,
  PATHNAME_LOGIN,
} from "$lib/constants.js";
import {
  getBatches,
  getBulkDownloadInfo,
  getBulkDownloadUrls,
  getDistinctColumnValues,
  getInstitutionStatus,
  getProjectInformation,
  getProjectProgress,
  getSampleMetadata,
  getUserDetails,
} from "./dataLoading.js";

const DASHBOARD_API_URL = "/dashboard-api";
const DATA_TYPE_METADATA = "metadata";
const INST_KEY_BATCH_DATE_PAIRS = [
  ["SomIns", "2021-05-20"],
  ["AnoIns", "2020-09-01"],
];
const INST_KEY_BATCH_DATE_OBJECTS = INST_KEY_BATCH_DATE_PAIRS.map(
  ([instKey, batchDate]) => ({
    "institution key": instKey,
    "batch date": batchDate,
  })
);

const DISTINCT_COLUMN_VALUES_STATE = {
  metadata: {
    serotype: ["1a", "1b", "NT"],
    country: ["doesn't", " mattter"],
  },
  "in silico": {
    adhP: ["doesn't", " mattter"],
  },
};
const FILTER_STATE = {
  metadata: {
    serotype: { values: ["1a", "1b"], exclude: true },
    country: { values: ["AU"] },
  },
  "qc data": { ctrl: { values: ["x", "y"] } },
  "in silico": { adhP: { values: ["x", "y"] } },
};
const MIME_TYPE_JSON = HTTP_HEADERS_JSON[HTTP_HEADER_CONTENT_TYPE];
const HEADERS_JSON = { get: () => MIME_TYPE_JSON };
const PATHNAME_NOT_LOGIN = "/samples";

const fetch = jest.fn();

jest.mock("$app/environment", () => ({
  get browser() {
    return true;
  },
}));

describe("authorization", () => {
  beforeEach(() => {
    delete global.location;
    global.location = { pathname: PATHNAME_NOT_LOGIN };
  });

  it("redirects to the login page if the response status is `401`", async () => {
    fetch.mockResolvedValueOnce({
      status: HTTP_STATUS_CODE_UNAUTHORIZED,
      headers: HEADERS_JSON,
      text: () => Promise.resolve(""),
      clone: function () {
        return this;
      },
    });

    await getBatches(fetch);

    expect(global.location.href).toBe(PATHNAME_LOGIN);
  });

  it("doesn't redirect to the login page if the response status is other than `401` and the MIME type isn't HTML", async () => {
    fetch.mockResolvedValueOnce({
      status: 200,
      ok: true,
      headers: HEADERS_JSON,
      text: () => Promise.resolve(""),
      json: () => Promise.resolve(""),
    });

    await getBatches(fetch);

    expect(global.location.href).not.toBe(PATHNAME_LOGIN);
  });

  it("redirects to the login page if the response has the HTML MIME type", async () => {
    fetch.mockResolvedValueOnce({
      headers: { get: () => MIME_TYPE_HTML },
      clone: function () {
        return this;
      },
    });

    await getBatches(fetch);

    expect(global.location.href).toBe(PATHNAME_LOGIN);
  });

  it("redirects to the login page if the response is HTML", async () => {
    fetch.mockResolvedValueOnce({
      headers: { get: () => {} },
      text: () => Promise.resolve("<!doctype html><title></title>"),
      clone: function () {
        return this;
      },
    });

    await getBatches(fetch);

    expect(global.location.href).toBe(PATHNAME_LOGIN);
  });

  it("doesn't redirect to the login page if the response isn't empty & isn't HTML", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => {} },
      text: () => Promise.resolve("not HTML"),
      json: () => Promise.resolve(""),
      clone: function () {
        return this;
      },
    });

    await getBatches(fetch);

    expect(global.location.href).not.toBe(PATHNAME_LOGIN);
  });

  it("redirects to the login page if the content type header & the response body are falsy", async () => {
    fetch.mockResolvedValueOnce({
      headers: { get: () => {} },
      text: () => Promise.resolve(null),
      clone: function () {
        return this;
      },
    });

    await getBatches(fetch);

    expect(global.location.href).toBe(PATHNAME_LOGIN);
  });
});

describe("login page", () => {
  afterAll(() => {
    delete global.location;
    global.location = { pathname: PATHNAME_NOT_LOGIN };
  });

  it("doesn't make a fetch request if the environment is the browser", async () => {
    delete global.location;
    global.location = { pathname: PATHNAME_LOGIN };
    fetch.mockClear();

    await getBatches(fetch);

    expect(fetch).not.toHaveBeenCalled();
  });

  it("makes a fetch request if the environment is not the browser", async () => {
    const browserSpy = jest.spyOn(environment, "browser", "get");
    const expectedPayload = "batches";
    browserSpy.mockReturnValueOnce(false);
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: HEADERS_JSON,
      json: () => Promise.resolve({ batches: expectedPayload }),
    });
    fetch.mockClear();

    const actualPayload = await getBatches(fetch);

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(actualPayload).toBe(expectedPayload);
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
      },
    },
    expectedResult: { some: "data" },
  },
  {
    fnName: "getBulkDownloadInfo",
    getResource: getBulkDownloadInfo,
    args: [
      {
        instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
        filter: {
          filterState: FILTER_STATE,
          distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE,
        },
        assemblies: true,
        annotations: false,
        reads: true,
      },
    ],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "qc data": { ctrl: ["x", "y"] },
          "in silico": { adhP: ["x", "y"] },
        },
        assemblies: true,
        annotations: false,
        reads: true,
      }),
    },
    expectedEndpoints: ["bulk_download_info"],
    responsePayload: "as is",
    expectedResult: "as is",
  },
  {
    fnName: "getBulkDownloadUrls",
    getResource: getBulkDownloadUrls,
    args: [
      {
        instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
        filter: {
          filterState: FILTER_STATE,
          distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE,
        },
        assemblies: true,
        annotations: false,
        reads: true,
        maxSamplesPerZip: 9,
      },
    ],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "qc data": { ctrl: ["x", "y"] },
          "in silico": { adhP: ["x", "y"] },
        },
        assemblies: true,
        annotations: false,
        reads: true,
        "max samples per zip": 9,
      }),
    },
    expectedEndpoints: ["bulk_download_urls"],
    responsePayload: "as is",
    expectedResult: "as is",
  },
  {
    fnName: "getDistinctColumnValues",
    getResource: getDistinctColumnValues,
    args: [
      {
        instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
        columns: [
          {
            name: "age_group",
            dataType: DATA_TYPE_METADATA,
          },
          {
            name: "adhP",
            dataType: "in silico",
          },
          {
            name: "serotype",
            dataType: DATA_TYPE_METADATA,
          },
        ],
        filter: {
          filterState: FILTER_STATE,
          distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE,
        },
      },
    ],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "qc data": { ctrl: ["x", "y"] },
          "in silico": { adhP: ["x", "y"] },
        },
        fields: [
          {
            "field type": DATA_TYPE_METADATA,
            "field names": ["age_group", "serotype"],
          },
          { "field type": "in silico", "field names": ["adhP"] },
        ],
      }),
    },
    expectedEndpoints: ["get_distinct_values"],
    responsePayload: {
      "distinct values": "inner response payload",
    },
    expectedResult: "inner response payload",
  },
  {
    fnName: "getInstitutionStatus",
    getResource: getInstitutionStatus,
    expectedEndpoints: [
      "get_institutions",
      "get_batches",
      "sequencing_status_summary",
      "pipeline_status_summary",
    ],
    responsePayload: {
      institutions: {
        CenRedSuf: { name: "Center for Reducing Suffering" },
        SenRes: { name: "Sentience Research" },
      },
      batches: {},
      sequencing_status: {
        CenRedSuf: { samples_received: 42 },
        SenRes: { samples_received: 99 },
      },
      pipeline_status: {},
    },
    expectedResult: [
      {
        batches: undefined,
        key: "CenRedSuf",
        name: "Center for Reducing Suffering",
        pipelineStatus: { sequencedSuccess: 42 },
        sequencingStatus: { samples_received: 42 },
      },
      {
        batches: undefined,
        key: "SenRes",
        name: "Sentience Research",
        pipelineStatus: { sequencedSuccess: 99 },
        sequencingStatus: { samples_received: 99 },
      },
    ],
  },
  {
    fnName: "getProjectInformation",
    getResource: getProjectInformation,
    expectedEndpoints: ["project"],
    responsePayload: {
      user_details: {
        type: "support",
      },
    },
    expectedResult: undefined,
  },
  {
    fnName: "getProjectProgress",
    getResource: getProjectProgress,
    expectedEndpoints: ["get_progress"],
    responsePayload: {
      progress_graph: {
        data: {
          date: "21.08.21",
          "samples received": 200,
          "samples sequenced": 50,
        },
      },
    },
    expectedResult: {
      datasets: [
        { name: "received", values: 200 },
        { name: "sequenced", values: 50 },
      ],
      dates: "21.08.21",
    },
  },
  {
    fnName: "getSampleMetadata",
    getResource: getSampleMetadata,
    args: [
      {
        instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
        filter: {
          filterState: FILTER_STATE,
          distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE,
        },
        columns: {
          metadata: ["some column"],
          "in silico": ["a column", "another column"],
        },
        numRows: 14,
        startRow: 2,
      },
    ],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "qc data": { ctrl: ["x", "y"] },
          "in silico": { adhP: ["x", "y"] },
        },
        "num rows": 14,
        "start row": 2,
        "metadata columns": ["some column"],
        "qc data": false,
        "in silico columns": ["a column", "another column"],
      }),
    },
    expectedEndpoints: ["get_metadata"],
    responsePayload: "as is",
    expectedResult: "as is",
  },
  {
    fnName: "getSampleMetadata",
    getResource: getSampleMetadata,
    args: [
      {
        instKeyBatchDatePairs: INST_KEY_BATCH_DATE_PAIRS,
        filter: {
          filterState: FILTER_STATE,
          distinctColumnValuesState: DISTINCT_COLUMN_VALUES_STATE,
        },
        numRows: 14,
        startRow: 2,
        asCsv: true,
      },
    ],
    expectedFetchOpts: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "sample filters": {
          batches: INST_KEY_BATCH_DATE_OBJECTS,
          metadata: { serotype: ["NT"], country: ["AU"] },
          "qc data": { ctrl: ["x", "y"] },
          "in silico": { adhP: ["x", "y"] },
        },
        "num rows": 14,
        "start row": 2,
        "as csv": true,
      }),
    },
    expectedEndpoints: ["get_metadata"],
    responsePayload: "blob",
    expectedResult: "blob",
  },
  {
    fnName: "getUserDetails",
    getResource: getUserDetails,
    expectedEndpoints: ["get_user_details"],
    responsePayload: {
      user_details: {
        type: "support",
      },
    },
    expectedResult: {
      type: "support",
    },
  },
])(
  "$fnName",
  ({
    getResource,
    args = [],
    expectedEndpoints,
    expectedFetchOpts,
    responsePayload,
    expectedResult,
  }) => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        headers: HEADERS_JSON,
        blob: () => Promise.resolve(responsePayload),
        json: () => Promise.resolve(responsePayload),
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
        expect([undefined, actualFetchOpts]).toContainEqual(expectedFetchOpts);
      });
    });

    it("returns result in the correct format", async () => {
      const result = await getResource(...args, fetch);

      expect(result).toEqual(expectedResult);
    });

    it("resolves 404 Not Found to `undefined`", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        headers: HEADERS_JSON,
      });

      await expect(getResource(...args, fetch)).resolves.toBeUndefined();
    });
  }
);
