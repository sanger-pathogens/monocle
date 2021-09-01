import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { getBatches } from "../../../dataLoading.js";
import DownloadPage from "./index.svelte";

global.fetch = () => {};

jest.mock("../../../dataLoading.js", () => ({
  getBatches: jest.fn(() => Promise.resolve()),
}));

it("shows the loading indicator", () => {
  const { getByLabelText } = render(DownloadPage);

  expect(getByLabelText("please wait")).toBeDefined();
});

it("shows an error message if fetching batches rejects", async () => {
  getBatches.mockRejectedValueOnce();

  const { getByText } = render(DownloadPage);

  await waitFor(() => {
    expect(getByText("An unexpected error occured during page loading. Please try again by reloading the page."))
      .toBeDefined();
  });
});

describe("once batches are fetched", () => {
  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(DownloadPage);

    await waitFor(() => {
      expect(queryByLabelText("please wait")).toBeNull();
    });
  });

  describe("batch selector", () => {
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

    beforeAll(() => {
      getBatches.mockResolvedValue(BATCHES_PAYLOAD);
    });

    it("displays a list of available batches and their institutions when clicked", async () => {
      const { findByRole, getByText } = render(DownloadPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      const institutions = Object.keys(BATCHES_PAYLOAD);
      institutions.forEach((institution) => {
        expect(getByText(institution)).toBeDefined();
      });
      BATCHES.forEach(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        expect(getByText(`${date}: ${name}${numSamplesText}`)).toBeDefined();
      });
    });

    it("selects and deselects all batches when the corresponding buttons are clicked", async () => {
      const roleButton = "button";
      const batchNamesWithData = BATCHES.map(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        return `${date}: ${name}${numSamplesText}`;
      });

      const { queryByText, findByRole, getByText } = render(DownloadPage);

      expectNoBatchesSelected(batchNamesWithData, queryByText);

      const selectAllBtn = await findByRole(roleButton, { name: "Select all" });
      fireEvent.click(selectAllBtn);

      await waitFor(() => {
        batchNamesWithData.forEach((batchName) => {
          expect(getByText(batchName)).toBeDefined();
        });
      });

      const deselectAllBtn = await findByRole(roleButton, { name: "Clear" });
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
