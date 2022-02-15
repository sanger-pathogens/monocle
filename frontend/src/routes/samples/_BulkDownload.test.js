import { act, fireEvent, render, waitFor } from "@testing-library/svelte";
import { get } from "svelte/store";
import { distinctColumnValuesStore, filterStore } from "./_stores.js";
import BulkDownload from "./_BulkDownload.svelte";
import {
  // The following import is needed for the mock to work.
  // eslint-disable-next-line no-unused-vars
  getBulkDownloadUrls
} from "$lib/dataLoading.js";

jest.mock("$lib/dataLoading.js", () => ({
  getBulkDownloadUrls: jest.fn(() => Promise.resolve([
    "/data/938479879", "/data/asdsd8f90fg", "/data/sdfasdf987", "/data/sdfsd0909", "/data/sdfsdfg98b98s09fd8"
  ]))
}));

const ANNOTATIONS_LABEL = "Annotations";
const ASSEMBLIES_LABEL = "Assemblies";
const FAKE_HEADER_ID = "section-header";
const LABEL_CONFIRM_BUTTON = "Confirm";
const LABEL_ESTIMATE_LOADING = "Estimating the download size. Please wait";
const ROLE_BUTTON = "button";
const ROLE_CHECKBOX = "checkbox";

const BATCHES = ["batch 1", "batch 2"];
const FORM_VALUES = { annotations: true, assemblies: true };

it("displays the data type checkboxes w/ assemblies and annotations checked", () => {
  const { getByRole, queryByRole } = render(BulkDownload, {
    batches: BATCHES,
    formValues: FORM_VALUES,
    ariaLabelledby: FAKE_HEADER_ID
  });

  expect(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL }).checked)
    .toBeTruthy();
  expect(getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL }).checked)
    .toBeTruthy();
  expect(queryByRole(ROLE_CHECKBOX, { name: /^Reads / }))
    .toBeNull();
});

it("enables the confirm button only when batches are passed and a data type is selected", async () => {
  const { component, getByRole } = render(BulkDownload, {
    formValues: { assemblies: false, annotations: false },
    ariaLabelledby: FAKE_HEADER_ID
  });

  let confirmButton = getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON });
  expect(confirmButton.disabled).toBeTruthy();

  component.$set({ batches: BATCHES });

  confirmButton = getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON });
  expect(confirmButton.disabled).toBeTruthy();

  const assembliesCheckbox = getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
  await fireEvent.click(assembliesCheckbox);

  confirmButton = getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON });
  expect(confirmButton.disabled).toBeFalsy();
});

it("displays the zero estimate when the download estimate isn't passed", () => {
  const { container } = render(BulkDownload, { formValues: FORM_VALUES, ariaLabelledby: FAKE_HEADER_ID });

  expect(container.querySelector("dl").textContent).toBe("Total size:0");
});

it("displays a loading icon when the download estimate isn't passed and the form is complete", () => {
  const { getByText } = render(BulkDownload, {
    batches: BATCHES,
    formValues: FORM_VALUES,
    ariaLabelledby: FAKE_HEADER_ID
  });

  expect(getByText(LABEL_ESTIMATE_LOADING)).toBeDefined();
});

describe("on form submit", () => {
  const INTERSTITIAL_PAGE_ENDPOINT = "/samples/download/";
  const LABEL_DOWNLOAD_LINKS_HEADER = "Download links";
  const LOADING_MESSAGE =
    "Please wait: generating a download link can take a while if thousands of samples are involved.";
  const ROLE_HEADING = "heading";
  const SELECTOR_MAIN_FORM_FIELDSET = "form > fieldset";
  const URL_SEPARATOR = "/";

  global.fetch = "fake fetch";

  beforeEach(() => {
    getBulkDownloadUrls.mockClear();
  });

  it("prevents submitting the form directly w/o clicking confirm if the form isn't comlpete", async () => {
    const { findByRole } = render(BulkDownload, { formValues: FORM_VALUES, ariaLabelledby: FAKE_HEADER_ID });
    global.confirm = jest.fn();

    const form = await findByRole("form");
    await fireEvent.submit(form);

    expect(confirm).not.toHaveBeenCalled();
    expect(getBulkDownloadUrls).not.toHaveBeenCalled();
  });

  it("disables the form", async () => {
    const { container, getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID
    });
    let containerFieldset;

    await waitFor(() => {
      containerFieldset = container.querySelector(SELECTOR_MAIN_FORM_FIELDSET);
      expect(containerFieldset.disabled).toBeFalsy();
      expect(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }).disabled)
        .toBeFalsy();
    });

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(containerFieldset.disabled).toBeTruthy();
    expect(containerFieldset.classList.contains("disabled"))
      .toBeTruthy();
    expect(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }).disabled)
      .toBeTruthy();
  });

  it("shows the loading indicator", async () => {
    const { getByLabelText, getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID
    });
    getBulkDownloadUrls.mockReturnValueOnce(new Promise(() => {}));

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(getByLabelText(LOADING_MESSAGE)).toBeDefined();
  });

  it("freezes the download estimate but only after having an estimate", async () => {
    const { component, container, getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID
    });
    const selectorDownloadEstimateValue = "dd";
    const downloadEstimate = { numSamples: 42, sizeZipped: "9.8GB" };
    const expectedDownloadEstimateText =
      `${downloadEstimate.numSamples} samples of ${downloadEstimate.sizeZipped}`;

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(container.querySelector(selectorDownloadEstimateValue).textContent)
      .toBe(LABEL_ESTIMATE_LOADING);

    await act(() => {
      component.$set({ downloadEstimate });
    });

    expect(container.querySelector(selectorDownloadEstimateValue).textContent)
      .toBe(expectedDownloadEstimateText);

    await act(() => {
      component.$set({ downloadEstimate: { numSamples: 998, sizeZipped: "70.2TB" } });
    });

    expect(container.querySelector(selectorDownloadEstimateValue).textContent)
      .toBe(expectedDownloadEstimateText);
  });

  it("requests and displays download links", async () => {
    const { getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID
    });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
    expect(getBulkDownloadUrls).toHaveBeenCalledWith({
        instKeyBatchDatePairs: BATCHES,
        filter: { filterState: get(filterStore), distinctColumnValues: get(distinctColumnValuesStore) },
        assemblies: true,
        annotations: true
      }, fetch);
    await waitFor(() => {
      expect(getByRole(ROLE_HEADING, { name: LABEL_DOWNLOAD_LINKS_HEADER }))
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
    const { getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID
    });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
    expect(getBulkDownloadUrls).toHaveBeenCalledWith({
        instKeyBatchDatePairs: BATCHES,
        filter: { filterState: get(filterStore), distinctColumnValues: get(distinctColumnValuesStore) },
        assemblies: true,
        annotations: true
      }, fetch);
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
    const { getByRole, queryByLabelText } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID
    });

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
  });

  describe("reset button", () => {
    const LABEL_RESET_BUTTON = "Reset";

    it("is displayed only after submit", async () => {
      const { queryByRole, getByRole } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID
      });

      expect(queryByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON }))
        .toBeNull();

      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      expect(getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON }))
        .toBeDefined();
    });

    it("resets the form", async () => {
      const component = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID
      });
      const { getByRole } = component;
      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON }));

      expectFormToBeReset(component);
    });

    it("can reset the form amid download link fetching", async () => {
      getBulkDownloadUrls.mockImplementationOnce(() => new Promise((resolve) => {
        setTimeout(() => resolve(["/data/938479879", "/data/asdsd8f90fg"]), 1000);
      }));
      const component = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID
      });
      const { queryByLabelText, getByRole } = component;
      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON }));

      expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
      expectFormToBeReset(component);
    });

    function expectFormToBeReset({ container, queryByRole, getByRole }) {
      expect(queryByRole(ROLE_HEADING, { name: LABEL_DOWNLOAD_LINKS_HEADER }))
        .toBeNull();
      expect(queryByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON }))
        .toBeNull();
      expect(container.querySelector(SELECTOR_MAIN_FORM_FIELDSET).disabled)
        .toBeFalsy();
      expect(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }).disabled)
        .toBeFalsy();
    }
  });

  describe("informs the user about an error", () => {
    const EXPECTED_ERROR_MSG = "Error while generating a download link. Please try again.";

    global.alert = jest.fn();

    afterEach(() => {
      global.alert.mockClear();
    });

    it("when fetching download links fails", async () => {
      const { getByRole } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID
      });
      getBulkDownloadUrls.mockRejectedValueOnce();

      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      expect(alert).toHaveBeenCalledTimes(1);
      expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
    });

    it("when no download links are returned from the server", async () => {
      const { getByRole } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID
      });
      getBulkDownloadUrls.mockResolvedValueOnce();

      fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      await waitFor(() => {
        expect(alert).toHaveBeenCalledTimes(1);
        expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
      });
    });

    it("hides the loading indicator", async () => {
      const { getByRole, queryByLabelText } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID
      });
      getBulkDownloadUrls.mockRejectedValueOnce();

      fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      await waitFor(() => {
        expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
      });
    });
  });
});
