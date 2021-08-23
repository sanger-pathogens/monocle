import { MONOCLE_URL } from "./dataLoading.js";
import { getSession, serverFetch } from "./hooks.js";

const DASHBOARD_API_INTERNAL_URL = "http://dash-api:5000/dashboard-api/";

global.fetch = jest.fn();

describe("getSession", () => {
  it("returns a session w/ a user w/ a role", async () => {
    const userRole = "support";
    global.fetch.mockClear();
    global.fetch.mockImplementation(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ user_details: { type: userRole } })
    }));

    const session = await getSession();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      `${DASHBOARD_API_INTERNAL_URL}get_user_details`);
    expect(session).toEqual({ user: { role: userRole } });
  });

  describe("sets the user role to `undefined` when", () => {
    it("the type field from user details is missing", async () => {
      global.fetch.mockImplementation(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(
          { user_details: {} })
      }));

      const { user: { role } } = await getSession(fetch);

      expect(role).toBeUndefined();
    });

    it("user details are missing", async () => {
      global.fetch.mockImplementation(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      }));

      const { user: { role } } = await getSession(fetch);

      expect(role).toBeUndefined();
    });

    it("the fetch request rejects", async () => {
      global.fetch.mockImplementation(() => Promise.resolve({
        ok: true,
        json: () => Promise.reject()
      }));

      const { user: { role } } = await getSession(fetch);

      expect(role).toBeUndefined();
    });

    it("the fetch request rejects", async () => {
      global.fetch.mockImplementation(() => Promise.resolve({
        ok: false
      }));

      const { user: { role } } = await getSession(fetch);

      expect(role).toBeUndefined();
    });
  });
});

describe("serverFetch", () => {
  global.Request = class {
    constructor(url) {
      this.url = url;
    }
  };

  beforeEach(() => {
    global.fetch.mockClear();
  });

  it("replaces the dashboard API URL w/ the internal URL when a request is from the Monocle origin", async () => {
    const request = { url: `${MONOCLE_URL}/dashboard-api/` };

    await serverFetch(request);

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const actualUrl = global.fetch.mock.calls[0][0].url;
    expect(actualUrl).toBe(DASHBOARD_API_INTERNAL_URL);
  });

  it("leaves a request untouched for domains other than Monocle's", async () => {
    const thirdPartyURL = "https://en.wikipedia.org/";

    await serverFetch({ url: thirdPartyURL });

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const actualUrl = global.fetch.mock.calls[0][0].url;
    expect(actualUrl).toBe(thirdPartyURL);
  });
});

