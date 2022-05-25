import { render, waitFor } from "@testing-library/svelte";
import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
import InterstitialPage from "./[token].svelte";

const DOWNLOAD_TOKEN = "some42token";
const LABEL_LOADING_INDICATOR =
  "Please wait: your download is being prepared. Large downloads may take a minute or two.";

const xmlHttpRequestMock = {
  addEventListener: jest.fn(),
  open: jest.fn(),
  send: jest.fn(),
  setRequestHeader: jest.fn(),
};

global.XMLHttpRequest = jest.fn(() => xmlHttpRequestMock);

it("shows the loading indicator", () => {
  const { getByLabelText } = render(InterstitialPage, {
    downloadToken: DOWNLOAD_TOKEN,
  });

  expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
});

it("sends the request to prepare download", () => {
  xmlHttpRequestMock.open.mockClear();
  xmlHttpRequestMock.send.mockClear();
  render(InterstitialPage, { downloadToken: DOWNLOAD_TOKEN });

  expect(xmlHttpRequestMock.open).toHaveBeenCalledTimes(1);
  expect(xmlHttpRequestMock.open).toHaveBeenCalledWith(
    "GET",
    `/data_download/${DOWNLOAD_TOKEN}?redirect=false`
  );
  expect(xmlHttpRequestMock.setRequestHeader).toHaveBeenCalledWith(
    "Content-Type",
    "application/json"
  );
  expect(xmlHttpRequestMock.send).toHaveBeenCalledTimes(1);
});

describe("on", () => {
  const EVENT_NAME_LOAD = "load";

  beforeEach(() => {
    xmlHttpRequestMock.addEventListener.mockClear();
  });

  describe("download prepared", () => {
    it("hides the loading indicator", async () => {
      const { queryByLabelText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const loadCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_LOAD
      )[1];

      loadCallback();

      await waitFor(() => {
        expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
      });
    });

    it("shows the download instructions and the download link resolved", async () => {
      const { container, getByRole } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const loadCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_LOAD
      )[1];
      const expectedUrl = `${global.location.origin}/download/url`;
      xmlHttpRequestMock.responseText = `{"download location":"${expectedUrl}"}`;

      loadCallback();

      await waitFor(() => {
        const instructions = container.getElementsByTagName("p")[0].textContent;
        expect(instructions).toBe(
          "Your download is ready. You can close this tab once the download starts. (If\n    you don't see a prompt to save the file, follow this download link.)"
        );
        expect(getByRole("link", { name: "download link" }).href).toBe(
          expectedUrl
        );
      });
    });
  });

  describe("error", () => {
    const EVENT_NAME_ERROR = "error";

    it("hides the loading indicator", async () => {
      const { queryByLabelText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const errorCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_ERROR
      )[1];

      errorCallback();

      await waitFor(() => {
        expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
      });
    });

    it("shows the timeout error on server timeout", async () => {
      const { getByText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const errorCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_ERROR
      )[1];
      xmlHttpRequestMock.status = 504;

      errorCallback();

      await waitFor(() => {
        expect(
          getByText(
            "Timeout error. Please reduce the download size and try again."
          )
        ).toBeDefined();
      });
    });

    it("shows a distinct error on any HTTP client error", async () => {
      const { getByText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const errorCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_ERROR
      )[1];
      xmlHttpRequestMock.status = 404;

      errorCallback();

      await waitFor(() => {
        expect(
          getByText(
            "Download might have expired. Please close the tab and start new download."
          )
        ).toBeDefined();
      });
    });

    it('detects an error as part of the "success" event and shows the generic error', async () => {
      const { getByText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const loadCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_LOAD
      )[1];
      xmlHttpRequestMock.status = 400;

      loadCallback();

      await waitFor(() => {
        expect(
          getByText(
            "Download might have expired. Please close the tab and start new download."
          )
        ).toBeDefined();
      });
    });

    it("shows an error on failing to parse the success response", async () => {
      const { container } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const errorCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_LOAD
      )[1];
      xmlHttpRequestMock.status = 200;
      xmlHttpRequestMock.responseText = 42;

      errorCallback();

      await waitFor(() => {
        expect(container.querySelector("p").innerHTML).toBe(
          `Server error. Please try again and <a href="mailto:${EMAIL_MONOCLE_HELP}">contact us</a> if the problem persists.`
        );
      });
    });

    it("shows the generic error on any other error", async () => {
      const { getByText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const errorCallback = xmlHttpRequestMock.addEventListener.mock.calls.find(
        (args) => args[0] === EVENT_NAME_ERROR
      )[1];
      xmlHttpRequestMock.status = 500;

      errorCallback();

      await waitFor(() => {
        expect(
          getByText(
            "Download error. Please try again by reloading the page or try to reduce the download size."
          )
        ).toBeDefined();
      });
    });
  });

  describe("cancel", () => {
    const EVENT_NAME_CANCEL = "abort";

    it("hides the loading indicator", async () => {
      const { queryByLabelText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const cancelCallback =
        xmlHttpRequestMock.addEventListener.mock.calls.find(
          (args) => args[0] === EVENT_NAME_CANCEL
        )[1];

      cancelCallback();

      await waitFor(() => {
        expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
      });
    });

    it("shows the cancellation text", async () => {
      const { getByText } = render(InterstitialPage, {
        downloadToken: DOWNLOAD_TOKEN,
      });
      const cancelCallback =
        xmlHttpRequestMock.addEventListener.mock.calls.find(
          (args) => args[0] === EVENT_NAME_CANCEL
        )[1];

      cancelCallback();

      await waitFor(() => {
        expect(
          getByText(
            "Download was cancelled. Refresh the page to start again or try to reduce the download size."
          )
        ).toBeDefined();
      });
    });
  });
});
