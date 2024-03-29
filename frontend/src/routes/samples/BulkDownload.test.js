import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { get } from "svelte/store";
import { distinctColumnValuesStore, filterStore } from "../stores.js";
import BulkDownload from "./BulkDownload.svelte";
import {
  // The following import is needed for the mock to work.
  // eslint-disable-next-line no-unused-vars
  getBulkDownloadUrls,
} from "$lib/dataLoading.js";

jest.mock("$lib/dataLoading.js", () => ({
  getBulkDownloadUrls: jest.fn(() =>
    Promise.resolve({
      download_urls: [
        "/data/938479879",
        "/data/asdsd8f90fg",
        "/data/sdfasdf987",
        "/data/sdfsd0909",
        "/data/sdfsdfg98b98s09fd8",
      ],
    })
  ),
}));

const CSS_SELECTOR_DOWNLOAD_SPLIT_SELECT = "dd select";
const DOWNLOAD_ESTIMATE = {
  numSamples: 42,
  sizeZipped: "9.8GB",
  sizePerZipOptions: [
    { sizePerZip: "9.8GB", maxSamplesPerZip: 52 },
    { sizePerZip: "1.1GB", maxSamplesPerZip: 6 },
  ],
};
const FAKE_HEADER_ID = "section-header";
const LABEL_ASSEMBLIES = "Assemblies";
const LABEL_CONFIRM_BUTTON = "Confirm";
const NUM_SAMPLES_DOWNLOAD_LIMIT = 99;
const RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_BEFORE_SUBMIT =
  /^⚠️ Cannot download more than/;
const ROLE_BUTTON = "button";
const ROLE_CHECKBOX = "checkbox";
const ROLE_OPTION = "option";

const BATCHES = ["batch 1", "batch 2"];
const FORM_VALUES = { annotations: true, assemblies: true };

it("displays the data type checkboxes w/ assemblies and annotations checked", () => {
  const { getByRole } = render(BulkDownload, {
    batches: BATCHES,
    formValues: FORM_VALUES,
    ariaLabelledby: FAKE_HEADER_ID,
  });

  expect(
    getByRole(ROLE_CHECKBOX, { name: LABEL_ASSEMBLIES }).checked
  ).toBeTruthy();
  expect(
    getByRole(ROLE_CHECKBOX, { name: "Annotations" }).checked
  ).toBeTruthy();
  expect(getByRole(ROLE_CHECKBOX, { name: /^Reads / }).checked).toBeFalsy();
});

it("enables the confirm button only when batches are passed and a data type is selected", async () => {
  const { component, getByRole } = render(BulkDownload, {
    formValues: { assemblies: false, annotations: false },
    ariaLabelledby: FAKE_HEADER_ID,
  });

  let confirmButton = getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON });
  expect(confirmButton.disabled).toBeTruthy();

  component.$set({ batches: BATCHES });

  confirmButton = getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON });
  expect(confirmButton.disabled).toBeTruthy();

  const assembliesCheckbox = getByRole(ROLE_CHECKBOX, {
    name: LABEL_ASSEMBLIES,
  });
  await fireEvent.click(assembliesCheckbox);

  confirmButton = getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON });
  expect(confirmButton.disabled).toBeFalsy();
});

it("displays `0`s for the estimate  when the download estimate isn't passed", () => {
  const { container } = render(BulkDownload, {
    formValues: FORM_VALUES,
    ariaLabelledby: FAKE_HEADER_ID,
  });

  expect(container.querySelector("dl").textContent).toBe(
    "Total size:0 Download split (keep the default unless your connection is\n            unstable):\n          0"
  );
});

it("displays a loading icon when the download estimate isn't passed and the form is complete", () => {
  const { getByText } = render(BulkDownload, {
    batches: BATCHES,
    formValues: FORM_VALUES,
    ariaLabelledby: FAKE_HEADER_ID,
  });

  expect(getByText("Estimating the download size. Please wait")).toBeDefined();
  expect(
    getByText("Estimating the size options for the download. Please wait")
  ).toBeDefined();
});

it("disables the size selector if there is only one option", () => {
  const sizePerZip = "10MB";
  const maxSamplesPerZip = 5;
  const { container, getByRole } = render(BulkDownload, {
    batches: BATCHES,
    formValues: FORM_VALUES,
    downloadEstimate: {
      ...DOWNLOAD_ESTIMATE,
      sizePerZipOptions: [{ sizePerZip, maxSamplesPerZip }],
    },
    ariaLabelledby: FAKE_HEADER_ID,
  });

  expect(
    container.querySelector(CSS_SELECTOR_DOWNLOAD_SPLIT_SELECT).disabled
  ).toBeTruthy();
  const numZips = Math.ceil(DOWNLOAD_ESTIMATE.numSamples / maxSamplesPerZip);
  expect(
    getByRole(ROLE_OPTION, {
      name: `${numZips} ZIP archives (${sizePerZip} each)`,
    })
  ).toBeDefined();
});

it("disables the size selector if there are no options", () => {
  const { container } = render(BulkDownload, {
    batches: BATCHES,
    formValues: FORM_VALUES,
    downloadEstimate: { ...DOWNLOAD_ESTIMATE, sizePerZipOptions: [] },
    ariaLabelledby: FAKE_HEADER_ID,
  });

  const sizeSelector = container.querySelector(
    CSS_SELECTOR_DOWNLOAD_SPLIT_SELECT
  );
  expect(sizeSelector.disabled).toBeTruthy();
  expect(sizeSelector.textContent).toBe("");
});

it("shows the warning if the estimate includes the sample download limit", async () => {
  const { component, getByText, queryByText } = render(BulkDownload, {
    batches: BATCHES,
    downloadEstimate: DOWNLOAD_ESTIMATE,
    formValues: FORM_VALUES,
    ariaLabelledby: FAKE_HEADER_ID,
  });

  expect(
    queryByText(RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_BEFORE_SUBMIT)
  ).toBeNull();

  await component.$set({
    downloadEstimate: {
      ...DOWNLOAD_ESTIMATE,
      numSamplesDownloadLimit: NUM_SAMPLES_DOWNLOAD_LIMIT,
    },
  });

  expect(getByText(RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_BEFORE_SUBMIT).textContent)
    .toBe(`⚠️ Cannot download more than ${NUM_SAMPLES_DOWNLOAD_LIMIT} samples.
      Add more filters to go below the limit.`);
});

describe("on form submit", () => {
  const DOWNLOAD_URL = "/data/some42token";
  const INTERSTITIAL_PAGE_ENDPOINT = "/samples/download/";
  const LABEL_DOWNLOAD_LINKS_HEADER = "Download links";
  const LABEL_RESET_BUTTON = "Reset";
  const LOADING_MESSAGE =
    "Please wait: generating ZIP download links can take a while if thousands of samples are involved.";
  const RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_AFTER_SUBMIT = /^⚠️ Only /;
  const ROLE_HEADING = "heading";
  const CSS_SELECTOR_DOWNLOAD_SIZE_ESTIMATE = "dd";
  const CSS_SELECTOR_MAIN_FORM_FIELDSET = "form > fieldset";
  const URL_SEPARATOR = "/";

  global.fetch = "fake fetch";

  beforeEach(() => {
    getBulkDownloadUrls.mockClear();
  });

  it("prevents submitting the form directly w/o clicking confirm if the form isn't comlpete", async () => {
    const { findByRole } = render(BulkDownload, {
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });
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
      ariaLabelledby: FAKE_HEADER_ID,
    });
    let containerFieldset;

    await waitFor(() => {
      containerFieldset = container.querySelector(
        CSS_SELECTOR_MAIN_FORM_FIELDSET
      );
      expect(containerFieldset.disabled).toBeFalsy();
    });

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(containerFieldset.disabled).toBeTruthy();
  });

  it("hides the download limit warning above the submit button", async () => {
    const { getByRole, queryByText } = render(BulkDownload, {
      batches: BATCHES,
      downloadEstimate: {
        ...DOWNLOAD_ESTIMATE,
        numSamplesDownloadLimit: NUM_SAMPLES_DOWNLOAD_LIMIT,
      },
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(
      queryByText(RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_BEFORE_SUBMIT)
    ).toBeNull();
  });

  it("shows the loading indicator", async () => {
    const { getByLabelText, getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });
    getBulkDownloadUrls.mockReturnValueOnce(new Promise(() => {}));

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(getByLabelText(LOADING_MESSAGE)).toBeDefined();
  });

  it("shows the post-submit warning if the download URL response include the sample download limit", async () => {
    const { getByRole, getByText, queryByText } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(
      queryByText(RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_AFTER_SUBMIT)
    ).toBeNull();

    getBulkDownloadUrls.mockResolvedValueOnce({
      download_urls: [DOWNLOAD_URL],
      num_samples_restricted_to: NUM_SAMPLES_DOWNLOAD_LIMIT,
    });
    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON }));
    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(getByText(RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_AFTER_SUBMIT).textContent)
      .toBe(`⚠️ Only 99 samples will be downloaded.
        Press the reset button and add more filters to go below the limit.`);
  });

  it("freezes the download estimate if batches change", async () => {
    const CSS_DOWNLOAD_SIZE_ESTIMATE_TEXT = `${DOWNLOAD_ESTIMATE.sizeZipped} (${
      DOWNLOAD_ESTIMATE.numSamples
    } sample${DOWNLOAD_ESTIMATE.numSamples === 1 ? "" : "s"}) `;
    const { component, container, getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );
    await component.$set({ downloadEstimate: DOWNLOAD_ESTIMATE });

    expect(
      container.querySelector(CSS_SELECTOR_DOWNLOAD_SIZE_ESTIMATE).textContent
    ).toBe(CSS_DOWNLOAD_SIZE_ESTIMATE_TEXT);

    await component.$set({ batches: ["anything"] });
    await component.$set({
      downloadEstimate: { numSamples: 998, sizeZipped: "70.2TB" },
    });

    expect(
      container.querySelector(CSS_SELECTOR_DOWNLOAD_SIZE_ESTIMATE).textContent
    ).toBe(CSS_DOWNLOAD_SIZE_ESTIMATE_TEXT);
  });

  it("freezes the total download size estimate if filters change", async () => {
    const CSS_DOWNLOAD_SIZE_ESTIMATE_TEXT = `${DOWNLOAD_ESTIMATE.sizeZipped} (${
      DOWNLOAD_ESTIMATE.numSamples
    } sample${DOWNLOAD_ESTIMATE.numSamples === 1 ? "" : "s"}) `;
    const { component, container, getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );
    await component.$set({ downloadEstimate: DOWNLOAD_ESTIMATE });

    expect(
      container.querySelector(CSS_SELECTOR_DOWNLOAD_SIZE_ESTIMATE).textContent
    ).toBe(CSS_DOWNLOAD_SIZE_ESTIMATE_TEXT);

    await filterStore.set({
      metadata: { someColumn: { values: [] } },
      "in silico": {},
    });
    await component.$set({
      downloadEstimate: { numSamples: 998, sizeZipped: "70.2TB" },
    });

    expect(
      container.querySelector(CSS_SELECTOR_DOWNLOAD_SIZE_ESTIMATE).textContent
    ).toBe(CSS_DOWNLOAD_SIZE_ESTIMATE_TEXT);

    filterStore.removeAllFilters();
  });

  it("displays the metadata download button", async () => {
    const { getByRole, queryByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });
    const labelMetadataDownload = "Download metadata";

    expect(
      queryByRole(ROLE_BUTTON, { name: labelMetadataDownload })
    ).toBeNull();

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(
      getByRole(ROLE_BUTTON, { name: labelMetadataDownload })
    ).toBeDefined();
  });

  it("requests and displays download links", async () => {
    const { getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
    expect(getBulkDownloadUrls).toHaveBeenCalledWith(
      {
        instKeyBatchDatePairs: BATCHES,
        filter: {
          filterState: get(filterStore),
          distinctColumnValuesState: get(distinctColumnValuesStore),
        },
        assemblies: true,
        annotations: true,
        maxSamplesPerZip: NaN,
      },
      fetch
    );
    await waitFor(() => {
      expect(
        getByRole(ROLE_HEADING, { name: LABEL_DOWNLOAD_LINKS_HEADER })
      ).toBeDefined();
      const downloadUrls = [
        "/data/938479879",
        "/data/asdsd8f90fg",
        "/data/sdfasdf987",
        "/data/sdfsd0909",
        "/data/sdfsdfg98b98s09fd8",
      ];
      const numLinks = downloadUrls.length;
      downloadUrls.forEach((downloadUrl, i) => {
        const downloadToken = downloadUrl.split(URL_SEPARATOR).pop();
        const downloadLink = getByRole("link", {
          name: `ZIP archive ${i + 1} of ${numLinks}`,
        });
        expect(downloadLink.href).toBe(
          `${global.location.origin}${INTERSTITIAL_PAGE_ENDPOINT}${downloadToken}`
        );
        expect(downloadLink.getAttribute("download")).toBeNull();
        expect(downloadLink.target).toBe("_blank");
      });
    });
  });

  it("requests and displays a download link when only one link is returned", async () => {
    getBulkDownloadUrls.mockResolvedValueOnce({
      download_urls: [DOWNLOAD_URL],
    });
    const { getByRole } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

    expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
    expect(getBulkDownloadUrls).toHaveBeenCalledWith(
      {
        instKeyBatchDatePairs: BATCHES,
        filter: {
          filterState: get(filterStore),
          distinctColumnValuesState: get(distinctColumnValuesStore),
        },
        assemblies: true,
        annotations: true,
        maxSamplesPerZip: NaN,
      },
      fetch
    );
    await waitFor(() => {
      const downloadToken = DOWNLOAD_URL.split(URL_SEPARATOR).pop();
      const downloadLink = getByRole("link", { name: "Download ZIP archive" });
      expect(downloadLink.href).toBe(
        `${global.location.origin}${INTERSTITIAL_PAGE_ENDPOINT}${downloadToken}`
      );
      expect(downloadLink.getAttribute("download")).toBeNull();
      expect(downloadLink.target).toBe("_blank");
    });
  });

  it("hides the loading indicator when a download link is displayed", async () => {
    const { getByRole, queryByLabelText } = render(BulkDownload, {
      batches: BATCHES,
      formValues: FORM_VALUES,
      ariaLabelledby: FAKE_HEADER_ID,
    });

    await fireEvent.click(
      getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
    );

    expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
  });

  describe("reset button", () => {
    it("is displayed only after submit", async () => {
      const { queryByRole, getByRole } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID,
      });

      expect(queryByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON })).toBeNull();

      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
      );

      expect(
        getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON })
      ).toBeDefined();
    });

    it("resets the form", async () => {
      const component = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID,
      });
      const { getByRole } = component;
      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
      );

      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON })
      );

      expectFormToBeReset(component);
    });

    it("can reset the form amid download link fetching", async () => {
      getBulkDownloadUrls.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(
              () => resolve(["/data/938479879", "/data/asdsd8f90fg"]),
              1000
            );
          })
      );
      const component = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID,
      });
      const { queryByLabelText, getByRole } = component;
      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
      );

      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON })
      );

      expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
      expectFormToBeReset(component);
    });

    it("updates the download estimate to the latest one", async () => {
      const { component, container, getByRole } = render(BulkDownload, {
        batches: BATCHES,
        downloadEstimate: DOWNLOAD_ESTIMATE,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID,
      });
      const latterDownloadEstimate = {
        numSamples: 19,
        sizeZipped: "2.2GB",
        sizePerZipOptions: [{ sizePerZip: "2.2GB", maxSamplesPerZip: 20 }],
      };

      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
      );
      await component.$set({ batches: ["anything"] });
      await component.$set({ downloadEstimate: latterDownloadEstimate });

      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON })
      );

      const CSS_latterDownloadEstimateText = `${latterDownloadEstimate.sizeZipped} (${latterDownloadEstimate.numSamples} samples) `;
      expect(
        container.querySelector(CSS_SELECTOR_DOWNLOAD_SIZE_ESTIMATE).textContent
      ).toBe(CSS_latterDownloadEstimateText);

      latterDownloadEstimate.sizePerZipOptions.forEach(
        ({ sizePerZip, maxSamplesPerZip }) => {
          const numZips = Math.ceil(
            latterDownloadEstimate.numSamples / maxSamplesPerZip
          );
          expect(
            getByRole(ROLE_OPTION, {
              name: `${numZips} ZIP archive${
                numZips === 1 ? "" : `s (${sizePerZip} each)`
              }`,
            })
          ).toBeDefined();
        }
      );
    });

    function expectFormToBeReset({
      container,
      queryByRole,
      queryByText,
      getByRole,
    }) {
      expect(
        queryByRole(ROLE_HEADING, { name: LABEL_DOWNLOAD_LINKS_HEADER })
      ).toBeNull();
      expect(queryByRole(ROLE_BUTTON, { name: LABEL_RESET_BUTTON })).toBeNull();
      expect(
        queryByText(RE_SAMPLE_DOWNLOAD_LIMIT_WARNING_AFTER_SUBMIT)
      ).toBeNull();
      expect(
        container.querySelector(CSS_SELECTOR_MAIN_FORM_FIELDSET).disabled
      ).toBeFalsy();
      expect(
        getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }).disabled
      ).toBeFalsy();
    }
  });

  describe("informs the user about an error", () => {
    const EXPECTED_ERROR_MSG =
      "Error while generating a download link. Please try again.";

    global.alert = jest.fn();

    afterEach(() => {
      global.alert.mockClear();
    });

    it("when fetching download links fails", async () => {
      const { getByRole } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID,
      });
      getBulkDownloadUrls.mockRejectedValueOnce();

      await fireEvent.click(
        getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON })
      );

      expect(alert).toHaveBeenCalledTimes(1);
      expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
    });

    it("when no download links are returned from the server", async () => {
      const { getByRole } = render(BulkDownload, {
        batches: BATCHES,
        formValues: FORM_VALUES,
        ariaLabelledby: FAKE_HEADER_ID,
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
        ariaLabelledby: FAKE_HEADER_ID,
      });
      getBulkDownloadUrls.mockRejectedValueOnce();

      fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CONFIRM_BUTTON }));

      await waitFor(() => {
        expect(queryByLabelText(LOADING_MESSAGE)).toBeNull();
      });
    });
  });
});
