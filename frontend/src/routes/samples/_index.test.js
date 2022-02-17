import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { get } from "svelte/store";
import debounce from "$lib/utils/debounce.js";
import { distinctColumnValuesStore, filterStore } from "./_stores.js";
import {
  getBatches,
  getBulkDownloadInfo,
  getInstitutions,
  getSampleMetadata
} from "$lib/dataLoading.js";
import DataViewerPage from "./index.svelte";

// Spy on `debounce` w/o changing its implementation. (`jest.spyOn` couldn't be used, as it works only w/ objects.)
jest.mock("$lib/utils/debounce.js", () => {
  const originalDebounce = jest.requireActual("$lib/utils/debounce.js");
  return {
    __esModule: true,
    default: jest.fn(originalDebounce.default)
  };
});

jest.mock("$lib/dataLoading.js", () => ({
  getBatches: jest.fn(() => Promise.resolve()),
  getBulkDownloadInfo: jest.fn(() => Promise.resolve({size: "42 TB", size_zipped: "7 TB"})),
  getInstitutions: jest.fn(() => Promise.resolve()),
  getSampleMetadata: jest.fn(() => Promise.resolve())
}));

it("shows the loading indicator", () => {
  const { getByLabelText } = render(DataViewerPage);

  expect(getByLabelText("please wait")).toBeDefined();
});

it("shows an error message if fetching batches rejects", async () => {
  getBatches.mockRejectedValueOnce();

  const { getByText } = render(DataViewerPage);

  await waitFor(() => {
    expect(getByText("An unexpected error occured during page loading. Please try again by reloading the page."))
      .toBeDefined();
  });
});

describe("once batches are fetched", () => {
  const BATCHES = [{
    name: "batch 1",
    date: "2021-07-30",
    number: 12
  }, {
    name: "batch 2",
    date: "2020-12-15",
    number: 32
  }, {
    name: "batch 3",
    date: "2021-07-21"
  }];
  const BATCHES_PAYLOAD = {
    FioRon: { deliveries: [BATCHES[0], BATCHES[1]] },
    UlmUni: { deliveries: [BATCHES[2]] }
  };
  const LABEL_SELECT_ALL = "Select all";
  const ROLE_BUTTON = "button";

  beforeAll(() => {
    getBatches.mockResolvedValue(BATCHES_PAYLOAD);
  });

  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(DataViewerPage);

    await waitFor(() => {
      expect(queryByLabelText("please wait")).toBeNull();
    });
  });

  it("removes all filters on clicking the filter removal button", async () => {
    const { findByRole, getByRole } = render(DataViewerPage);
    filterStore.set({ metadata: { someColumn: {} }, "in silico": {}, "qc data": {} });
    const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
    await fireEvent.click(selectAllBtn);
    const filterRemovalLabel = /^Remove all filters/;
    global.confirm = () => true;

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: filterRemovalLabel }));

    expect(get(filterStore)).toEqual({ metadata: {}, "in silico": {}, "qc data": {} });
    expect(getByRole(ROLE_BUTTON, { name: filterRemovalLabel }).disabled)
      .toBeTruthy();
  });

  it("disables the filter removal button on batches change", async () => {
    const filterRemovalLabel = /^Remove all filters/;
    const { findByRole, getByRole } = render(DataViewerPage);
    const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
    await fireEvent.click(selectAllBtn);
    filterStore.update((filters) => {
      filters.metadata.someColumn = { values: ["some value"] };
      return filters;
    });

    await waitFor(() => {
      expect(getByRole(ROLE_BUTTON, { name: filterRemovalLabel }).disabled)
        .toBeFalsy();
    });

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: "Clear" }));
    await fireEvent.click(selectAllBtn);

    expect(getByRole(ROLE_BUTTON, { name: filterRemovalLabel }).disabled)
      .toBeTruthy();
  });

  describe("batch selector", () => {
    it("displays a list of available batches and their institutions when clicked", async () => {
      const institutionsPayload = Object.keys(BATCHES_PAYLOAD)
        .reduce((accum, institutionKey) => {
          accum[institutionKey] = { name: `full name of ${institutionKey}` };
          return accum;
        }, {});
      getInstitutions.mockResolvedValueOnce(institutionsPayload);
      const { findByRole, getByText } = render(DataViewerPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      Object.values(institutionsPayload).forEach(({ name: institutionName }) => {
        expect(getByText(institutionName)).toBeDefined();
      });
      BATCHES.forEach(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        expect(getByText(`${date}: ${name}${numSamplesText}`)).toBeDefined();
      });
    });

    it("displays institution keys if full names aren't available", async () => {
      getInstitutions.mockRejectedValueOnce();
      const { findByRole, getByText } = render(DataViewerPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      Object.keys(BATCHES_PAYLOAD).forEach((institutionKey) => {
        expect(getByText(institutionKey)).toBeDefined();
      });
    });

    it("ignores institutions w/ no batches", async () => {
      const institutionWithoutBatches = "XyzUni";
      const batchesPayload = {
        ...BATCHES_PAYLOAD,
        [institutionWithoutBatches]: { _ERROR: "no batches" }
      };
      getBatches.mockResolvedValueOnce(batchesPayload);
      const { findByRole, getByText, queryByText } = render(DataViewerPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      expect(queryByText(institutionWithoutBatches)).toBeNull();
      Object.keys(BATCHES_PAYLOAD).forEach((institutionKey) => {
        expect(getByText(institutionKey)).toBeDefined();
      });
    });

    it("selects and deselects all batches when the corresponding buttons are clicked", async () => {
      const batchNamesWithData = BATCHES.map(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        return `${date}: ${name}${numSamplesText}`;
      });

      const { queryByText, findByRole, getByText } = render(DataViewerPage);

      expectNoBatchesSelected(batchNamesWithData, queryByText);

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);

      await waitFor(() => {
        batchNamesWithData.forEach((batchName) => {
          expect(getByText(batchName)).toBeDefined();
        });
      });

      const deselectAllBtn = await findByRole(ROLE_BUTTON, { name: "Clear" });
      await fireEvent.click(deselectAllBtn);

      expectNoBatchesSelected(batchNamesWithData, queryByText);
    });

    function expectNoBatchesSelected(batchNamesWithData, queryByText) {
      batchNamesWithData.forEach((batchName) => {
        expect(queryByText(batchName)).toBeNull();
      });
    }
  });

  describe("bulk download button", () => {
    const ALT_ZIP_SIZE = "13 TB";
    const LABEL_ASSEMBLIES = "Assemblies";
    const LABEL_LOADING_DOWNLOAD_BUTTON = "Download samples";
    const ROLE_CHECKBOX = "checkbox";

    it("displays a loading indicator as part of its label while download estimate is being fetched", async () => {
      const { findByRole, getByRole } = render(DataViewerPage);

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      await fireEvent.click(selectAllBtn);

      expect(getByRole(ROLE_BUTTON, { name: LABEL_LOADING_DOWNLOAD_BUTTON }).querySelector(".spinner"))
        .not.toBeNull();
    });

    it("updates the download estimate if selected batches change", async () => {
      const { findByRole, getByRole } = render(DataViewerPage);

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);

      await waitFor(() => {
        expect(getByRole(ROLE_BUTTON, { name: "Download samples of size 7 TB" }))
          .toBeDefined();
      });

      const clearBtn = await findByRole(ROLE_BUTTON, { name: "Clear" });
      await fireEvent.click(clearBtn);
      getBulkDownloadInfo.mockResolvedValueOnce({ size: "42 TB", size_zipped: ALT_ZIP_SIZE });
      fireEvent.click(selectAllBtn);

      await waitFor(() => {
        expect(getByRole(ROLE_BUTTON, { name: `Download samples of size ${ALT_ZIP_SIZE}` }))
          .toBeDefined();
      });
    });

    it("updates the download estimate if selected data types change", async () => {
      const { findByRole, getByRole } = render(DataViewerPage);
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);
      let downloadButton;

      await waitFor(() => {
        downloadButton = getByRole(ROLE_BUTTON, { name: "Download samples of size 7 TB" });
        expect(downloadButton).toBeDefined();
      });

      // Open the bulk download dialog.
      await fireEvent.click(downloadButton);
      getBulkDownloadInfo.mockResolvedValueOnce({ size: "42 TB", size_zipped: ALT_ZIP_SIZE });
      await fireEvent.click(getByRole(ROLE_CHECKBOX, { name: LABEL_ASSEMBLIES }));

      await waitFor(() => {
        expect(getByRole(ROLE_BUTTON, { name: `Download samples of size ${ALT_ZIP_SIZE}` }))
          .toBeDefined();
      });
    });

    it("debounces the download estimate request", async () => {
      const { findByRole, getByRole } = render(DataViewerPage);
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      await fireEvent.click(selectAllBtn);
      // Open the bulk download dialog.
      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOADING_DOWNLOAD_BUTTON }));
      debounce.mockClear();

      fireEvent.click(getByRole(ROLE_CHECKBOX, { name: LABEL_ASSEMBLIES }));
      await fireEvent.click(getByRole(ROLE_CHECKBOX, { name: LABEL_ASSEMBLIES }));

      expect(debounce).toHaveBeenCalledTimes(1);
    });

    it("doesn't request download estimate if the form isn't complete", async () => {
      const { findByRole, getByRole } = render(DataViewerPage);
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      await fireEvent.click(selectAllBtn);
      // Open the bulk download dialog.
      await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOADING_DOWNLOAD_BUTTON }));

      // Deselect data types.
      await fireEvent.click(getByRole(ROLE_CHECKBOX, { name: LABEL_ASSEMBLIES }));
      getBulkDownloadInfo.mockClear();
      await fireEvent.click(getByRole(ROLE_CHECKBOX, { name: "Annotations" }));

      expect(getBulkDownloadInfo).not.toHaveBeenCalled();
    });
  });

  describe("metadata download button", () => {
    const DOWNLOAD_URL = "some/url";
    const LABEL_METADATA_DOWNLOAD_BUTTON = "Download metadata";

    global.URL.createObjectURL = () => DOWNLOAD_URL;
    global.URL.revokeObjectURL = () => {};

    it("requests metadata CSV on click", async () => {
      const { findByRole } = render(DataViewerPage);
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);
      getSampleMetadata.mockClear();

      const metadataDownloadButton = await findByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON });
      await fireEvent.click(metadataDownloadButton);

      expect(getSampleMetadata).toHaveBeenCalledTimes(1);
      expect(getSampleMetadata).toHaveBeenCalledWith(
        { asCsv: true,
          instKeyBatchDatePairs: [
            ["FioRon", BATCHES[0].date],
            ["FioRon", BATCHES[1].date],
            ["UlmUni", BATCHES[2].date] ],
          filter: { filterState: get(filterStore), distinctColumnValues: get(distinctColumnValuesStore) }
        },
        fetch);
    });

    it("is disabled and shows the loading text while waiting for the metadata CSV", async () => {
      const { findByRole, getByRole } = render(DataViewerPage);
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);

      const metadataDownloadButton = await findByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON });
      await fireEvent.click(metadataDownloadButton);

      expect(metadataDownloadButton.disabled).toBeTruthy();
      expect(getByRole(ROLE_BUTTON, { name: "Preparing download" }))
        .toBeDefined();
    });

    it("hides the loading state, frees resources, and downloads metadata CSV once it's prepared", async () => {
      const hiddenDownloadLink = document.createElement("a");
      hiddenDownloadLink.click = jest.fn();
      const createAnchorElement = () => hiddenDownloadLink;
      const { findByRole } = render(DataViewerPage, {
        injectedCreateAnchorElement: createAnchorElement
      });
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);
      global.URL.revokeObjectURL = jest.fn();

      const metadataDownloadButton = await findByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON });
      fireEvent.click(metadataDownloadButton);

      await waitFor(() => {
        expect(hiddenDownloadLink.click).toHaveBeenCalledTimes(1);
        expect(hiddenDownloadLink.href).toBe(`${global.location.href}${DOWNLOAD_URL}`);
        expect(hiddenDownloadLink.download).toBe("monocle-sample-metadata.csv");
        expect(hiddenDownloadLink.style.display).toBe("none");
        expect(URL.revokeObjectURL).toHaveBeenCalledTimes(1);
        expect(URL.revokeObjectURL).toHaveBeenCalledWith(DOWNLOAD_URL);
        expect(hiddenDownloadLink.parentElement).toBeNull();
      });
    });

    it("frees resources on download fail", async () => {
      const hiddenDownloadLink = document.createElement("a");
      hiddenDownloadLink.click = () => {
        throw "some error";
      };
      const createAnchorElement = () => hiddenDownloadLink;
      const { findByRole } = render(DataViewerPage, {
        injectedCreateAnchorElement: createAnchorElement
      });
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: LABEL_SELECT_ALL });
      fireEvent.click(selectAllBtn);
      global.URL.revokeObjectURL = jest.fn();

      const metadataDownloadButton = await findByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON });
      fireEvent.click(metadataDownloadButton);

      await waitFor(() => {
        expect(URL.revokeObjectURL).toHaveBeenCalledWith(DOWNLOAD_URL);
        expect(hiddenDownloadLink.parentElement).toBeNull();
      });
    });
  });
});
