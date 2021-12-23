import { fireEvent, render, waitFor } from "@testing-library/svelte";
import BulkDownload from "./_BulkDownload.svelte";
import debounce from "$lib/utils/debounce.js";
import {
  // The next import is needed for the mock to work.
  // eslint-disable-next-line no-unused-vars
  getBulkDownloadInfo,
  getBulkDownloadUrls
} from "$lib/dataLoading.js";

// Spy on `debounce` w/o changing its implementation. (`jest.spyOn` couldn't be used, as it works only w/ objects.)
jest.mock("$lib/utils/debounce.js", () => {
  const originalDebounce = jest.requireActual("$lib/utils/debounce.js");
  return {
    __esModule: true,
    default: jest.fn(originalDebounce.default)
  };
});

jest.mock("$lib/dataLoading.js", () => ({
  getBulkDownloadInfo: jest.fn(() => Promise.resolve({size: "42 TB", size_zipped: "7 TB"})),
  getBulkDownloadUrls: jest.fn(() => Promise.resolve([
    "/data/938479879", "/data/asdsd8f90fg", "/data/sdfasdf987", "/data/sdfsd0909", "/data/sdfsdfg98b98s09fd8"
  ]))
}));

const ANNOTATIONS_LABEL = "Annotations";
const ASSEMBLIES_LABEL = "Assemblies";
const CONFIRM_BUTTON_LABEL = "Confirm";
const EXPECTED_DOWNLOAD_ESTIMATE_TEXT = "7 TB";
const FAKE_HEADER_ID = "section-header";
const ROLE_BUTTON = "button";
const ROLE_CHECKBOX = "checkbox";
const ROLE_OPTION = "option";

const BATCHES = ["batch 1", "batch 2"];

it("displays the data type checkboxes w/ assemblies and annotations checked", () => {
  const { getByRole, queryByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

  expect(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL }).checked)
    .toBeTruthy();
  expect(getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL }).checked)
    .toBeTruthy();
  expect(queryByRole(ROLE_CHECKBOX, { name: /^Reads / }))
    .toBeNull();
});

it("enables the confirm button only when batch are passed and a data type is selected", async () => {
  const { component, getByRole } = render(BulkDownload, { ariaLabelledby: FAKE_HEADER_ID });
  // Deselect data types:
  let assembliesCheckbox = getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
  fireEvent.click(assembliesCheckbox);
  const annotationsCheckbox = getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL });
  fireEvent.click(annotationsCheckbox);

  let confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
  expect(confirmButton.disabled).toBeTruthy();

  component.$set({ batches: BATCHES });

  confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
  expect(confirmButton.disabled).toBeTruthy();

  assembliesCheckbox = getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
  await fireEvent.click(assembliesCheckbox);

  confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
  expect(confirmButton.disabled).toBeFalsy();
});

it("updates the download estimate if selected batches change", async () => {
  const { component, getByRole, queryByRole } = render(BulkDownload, { ariaLabelledby: FAKE_HEADER_ID });

  let downloadEstimateElement = queryByRole(ROLE_OPTION);
  expect(downloadEstimateElement).toBeNull();

  component.$set({ batches: BATCHES });

  await waitFor(() => {
    downloadEstimateElement = getByRole(ROLE_OPTION);
    expect(downloadEstimateElement.textContent).toBe(EXPECTED_DOWNLOAD_ESTIMATE_TEXT);
  });
});

it("updates the download estimate if selected data types change", async () => {
  const { getByRole, queryByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

  // Deselect data types.
  fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));
  fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL }));

  await waitFor(() => {
    const downloadEstimateElement = queryByRole(ROLE_OPTION);
    expect(downloadEstimateElement).toBeNull();
  });

  fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));

  await waitFor(() => {
    const downloadEstimateElement = getByRole(ROLE_OPTION);
    expect(downloadEstimateElement.textContent).toBe(EXPECTED_DOWNLOAD_ESTIMATE_TEXT);
  });
});

it("debounces the download estimate request", async () => {
  debounce.mockClear();
  const { getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

  await waitFor(() => {
    expect(debounce).toHaveBeenCalledTimes(1);
  });

  debounce.mockClear();
  fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));
  await fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));

  expect(debounce).toHaveBeenCalledTimes(1);
});

describe("on form submit", () => {
  const INTERSTITIAL_PAGE_ENDPOINT = "/samples/download/";
  const LOADING_MESSAGE =
    "Please wait: generating a download link can take a while if thousands of samples are involved.";
  const URL_SEPARATOR = "/";

  global.fetch = "fake fetch";

  beforeEach(() => {
    global.confirm = () => true;
    getBulkDownloadUrls.mockClear();
  });

  it("prevents submitting the form directly w/o clicking confirm if the form isn't comlpete", async () => {
    const { findByRole } = render(BulkDownload, { ariaLabelledby: FAKE_HEADER_ID });
    global.confirm = jest.fn();

    const form = await findByRole("form");
    await fireEvent.submit(form);

    expect(confirm).not.toHaveBeenCalled();
    expect(getBulkDownloadUrls).not.toHaveBeenCalled();
  });

  it("asks for confirmation", async () => {
    global.confirm = jest.fn(() => false);
    const { getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

    expect(confirm).toHaveBeenCalledTimes(1);
    expect(confirm).toHaveBeenCalledWith("You won't be able to change the download parameters if you proceed.");
  });

  it("disables the form", async () => {
    const { container, getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });
    let containerFieldset;

    await waitFor(() => {
      containerFieldset = container.querySelector("form > fieldset");
      expect(containerFieldset.disabled).toBeFalsy();
    });

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

    expect(containerFieldset.disabled).toBeTruthy();
    expect(containerFieldset.classList.contains("disabled"))
      .toBeTruthy();
  });

  it("shows the loading indicator", async () => {
    const { getByLabelText, getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });
    getBulkDownloadUrls.mockReturnValueOnce(new Promise(() => {}));

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

    expect(getByLabelText(LOADING_MESSAGE)).toBeDefined();
  });

  it("requests and displays download links", async () => {
    const { getByText, getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

    expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
    expect(getBulkDownloadUrls).toHaveBeenCalledWith(
      BATCHES,
      {assemblies: true, annotations: true},
      fetch);
    await waitFor(() => {
      const ariaRoleHeading = "heading";
      expect(getByRole(ariaRoleHeading, { name: "Download links" }))
        .toBeDefined();
      const downloadUrls = [
        "/data/938479879", "/data/asdsd8f90fg", "/data/sdfasdf987", "/data/sdfsd0909", "/data/sdfsdfg98b98s09fd8"
      ];
      const numLinks = downloadUrls.length;
      downloadUrls.forEach((downloadUrl, i) => {
        const downloadToken = downloadUrl.split(URL_SEPARATOR).pop();
        const downloadLink = getByRole("link", { name: `ZIP archive ${i + 1} of ${numLinks}` });
        expect(downloadLink.href).toBe(
          `${global.location.origin}${INTERSTITIAL_PAGE_ENDPOINT}${downloadToken}`);
        expect(downloadLink.getAttribute("download")).toBeNull();
        expect(downloadLink.target).toBe("_blank");
      });
    });
  });

  it("requests and displays a download link when only one link is returned", async () => {
    const downloadUrl = "/data/some42token";
    getBulkDownloadUrls.mockResolvedValueOnce([downloadUrl]);
    const { getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

    expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
    expect(getBulkDownloadUrls).toHaveBeenCalledWith(
      BATCHES,
      {assemblies: true, annotations: true},
      fetch);
    await waitFor(() => {
      const downloadToken = downloadUrl.split(URL_SEPARATOR).pop();
      const downloadLink = getByRole("link", { name: "Download ZIP archive" });
      expect(downloadLink.href).toBe(
        `${global.location.origin}${INTERSTITIAL_PAGE_ENDPOINT}${downloadToken}`);
      expect(downloadLink.getAttribute("download")).toBeNull();
      expect(downloadLink.target).toBe("_blank");
    });
  });

  it("hides the loading indicator when a download link is displayed", async () => {
    const { getByRole, queryByLabelText } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

    expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
  });

  describe("informs the user about an error", () => {
    const EXPECTED_ERROR_MSG = "Error while generating a download link. Please try again.";

    global.alert = jest.fn();

    afterEach(() => {
      global.alert.mockClear();
    });

    it("when fetching download links fails", async () => {
      const { getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });
      getBulkDownloadUrls.mockRejectedValueOnce();

      await fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

      expect(alert).toHaveBeenCalledTimes(1);
      expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
    });

    it("when no download links are returned from the server", async () => {
      const { getByRole } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });
      getBulkDownloadUrls.mockResolvedValueOnce();

      fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

      await waitFor(() => {
        expect(alert).toHaveBeenCalledTimes(1);
        expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
      });
    });

    it("hides the loading indicator", async () => {
      const { getByRole, queryByLabelText } = render(BulkDownload, { batches: BATCHES, ariaLabelledby: FAKE_HEADER_ID });
      getBulkDownloadUrls.mockRejectedValueOnce();

      fireEvent.click(getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }));

      await waitFor(() => {
        expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
      });
    });
  });
});
