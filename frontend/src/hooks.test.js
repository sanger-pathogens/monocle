import { MONOCLE_URL } from "./dataLoading.js";
import { serverFetch } from "./hooks.js";

describe("serverFetch", () => {
  global.Request = class {
    constructor(url) {
      this.url = url;
    }
  };

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  it("replaces the dashboard API URL w/ the internal URL when a request is from the Monocle origin", async () => {
    const request = { url: `${MONOCLE_URL}/dashboard-api/` };

    await serverFetch(request);

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const actualUrl = global.fetch.mock.calls[0][0].url;
    expect(actualUrl).toBe("http://dash-api/dashboard-api/");
  });

  it("leaves a request untouched for domains other than Monocle's", async () => {
    const thirdPartyURL = "https://en.wikipedia.org/";

    await serverFetch({ url: thirdPartyURL });

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const actualUrl = global.fetch.mock.calls[0][0].url;
    expect(actualUrl).toBe(thirdPartyURL);
  });
});

