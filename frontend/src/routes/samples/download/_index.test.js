import { fireEvent, render, waitFor } from "@testing-library/svelte";
import {
  getBatches,
  getBulkDownloadInfo,
  getBulkDownloadUrls,
  getInstitutions,
  getSampleMetadata
} from "$lib/dataLoading.js";
import DataViewerPage from "./index.svelte";

jest.mock("$lib/dataLoading.js", () => ({
  // FIXME: check for redundancy
  getBatches: jest.fn(() => Promise.resolve()),
  getBulkDownloadInfo: jest.fn(() => Promise.resolve({size: "42 TB", size_zipped: "7 TB"})),
  getBulkDownloadUrls: jest.fn(() => Promise.resolve(["fake-download-url"])),
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
      const batches_payload = {
        ...BATCHES_PAYLOAD,
        [institutionWithoutBatches]: { _ERROR: "no batches" }
      };
      getBatches.mockResolvedValueOnce(batches_payload);
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

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: "Select all" });
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
});
