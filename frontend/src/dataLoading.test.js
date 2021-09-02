import {
  getInstitutionStatus,
  getProjectProgress,
  getUserDetails
} from "./dataLoading.js";

const DASHBOARD_API_URL = "dashboard-api";

const fetch = jest.fn();

describe.each([
  {
    fnName: "getInstitutionStatus",
    getResource: getInstitutionStatus,
    expectedEndpoints: ["get_institutions", "get_batches", "sequencing_status_summary", "pipeline_status_summary"],
    payload: {
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
    payload: {
      progress_graph: {
        data: { date: "21.08.21", "samples received": 200, "samples sequenced": 50 },
      }
    },
    expectedResult: {
      datasets: [
        { name: "samples received", values: 200 },
        { name: "samples sequenced", values: 50}
      ],
      dates: "21.08.21"
    }
  },
  {
    fnName: "getUserDetails",
    getResource: getUserDetails,
    expectedEndpoints: ["get_user_details"],
    payload: {
      user_details: {
        type: "support"
      }
    },
    expectedResult: {
      type: "support"
    }
  }
])("$fnName", ({ getResource, expectedEndpoints, payload, expectedResult }) => {
  beforeEach(() => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload)
    });
  });

  it("fetches the data from the correct endpoints", async () => {
    fetch.mockClear();

    await getResource(fetch);

    expect(fetch).toHaveBeenCalledTimes(expectedEndpoints.length);
    expectedEndpoints.forEach((expectedEndpoint) => {
      expect(fetch).toHaveBeenCalledWith(`${DASHBOARD_API_URL}/${expectedEndpoint}`);
    });
  });

  it("returns result in the correct format", async () => {
    const result = await getResource(fetch);

    expect(result).toEqual(expectedResult);
  });
});
