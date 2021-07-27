import {
  MONOCLE_URL,
  getInstitutionStatus,
  getProjectProgress,
  getUserRole
} from "./dataLoading.js";

const DASHBOARD_API_URL = `${MONOCLE_URL}/dashboard-api`;
const USER_ROLE = "support";

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
    fnName: "getUserRole",
    getResource: getUserRole,
    expectedEndpoints: ["get_user_details"],
    payload: {
      user_details: {
        type: USER_ROLE,
      }
    },
    expectedResult: USER_ROLE
  }
])("$fnName", ({ getResource, expectedEndpoints, payload, expectedResult }) => {
  it("fetches the data from the correct endpoints", async () => {
    fetch.mockClear();
    fetch.mockImplementation(() => Promise.resolve({ ok: false }));

    await getResource(fetch);

    expect(fetch).toHaveBeenCalledTimes(expectedEndpoints.length);
    expectedEndpoints.forEach((expectedEndpoint) => {
      expect(fetch).toHaveBeenCalledWith(`${DASHBOARD_API_URL}/${expectedEndpoint}`);
    });
  });

  it("returns result in the correct format", async () => {
    fetch.mockImplementation(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(payload)
    }));

    const result = await getResource(fetch);

    expect(result).toEqual(expectedResult);
  });
});

describe("`getUserRole` returns `undefined`", () => {
  it("when the type field from user details is missing", async () => {
    fetch.mockImplementation(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(
        { user_details: {} })
    }));

    const userRole = await getUserRole(fetch);

    expect(userRole).toBeUndefined();
  });

  it("when user details are missing", async () => {
    fetch.mockImplementation(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({})
    }));

    const userRole = await getUserRole(fetch);

    expect(userRole).toBeUndefined();
  });

  it("when the fetch request rejects", async () => {
    fetch.mockImplementation(() => Promise.resolve({
      ok: true,
      json: () => Promise.reject()
    }));

    const userRole = await getUserRole(fetch);

    expect(userRole).toBeUndefined();
  });

  it("when the fetch request rejects", async () => {
    fetch.mockImplementation(() => Promise.resolve({
      ok: false
    }));

    const userRole = await getUserRole(fetch);

    expect(userRole).toBeUndefined();
  });
});
