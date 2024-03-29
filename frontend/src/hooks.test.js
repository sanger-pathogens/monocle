import { externalFetch, handle } from "./hooks.js";

const DASHBOARD_API_INTERNAL_URL = "http://dash-api:5000/dashboard-api/";

global.fetch = jest.fn();

it("disables SSR", async () => {
  const event = "some event";
  const resolve = jest.fn();

  await handle({ event, resolve });

  expect(resolve).toHaveBeenCalledTimes(1);
  expect(resolve).toHaveBeenCalledWith(event, { ssr: false });
});

describe("externalFetch", () => {
  global.Request = class {
    constructor(url) {
      this.url = url;
    }
  };

  beforeEach(() => {
    global.fetch.mockClear();
  });

  it("replaces the dashboard API URL w/ the internal URL when a request is from the Monocle origin", async () => {
    const request = { url: "http://monocle.pam.sanger.ac.uk/dashboard-api/" };

    await externalFetch(request);

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const actualUrl = global.fetch.mock.calls[0][0].url;
    expect(actualUrl).toBe(DASHBOARD_API_INTERNAL_URL);
  });

  it("leaves a request untouched for domains other than Monocle's", async () => {
    const thirdPartyURL = "https://en.wikipedia.org/";

    await externalFetch({ url: thirdPartyURL });

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const actualUrl = global.fetch.mock.calls[0][0].url;
    expect(actualUrl).toBe(thirdPartyURL);
  });
});
