import { render, waitFor } from "@testing-library/svelte";
import SampleMetadataViewer from "./_SampleMetadataViewer.svelte";
import debounce from "$lib/utils/debounce.js"
import { getSampleMetadata } from "$lib/dataLoading.js";

// A workaround for Jest's `spyOn` working only for object methods.
const debounceRef = { debounce };

const BATCHES = ["some batches"];
const ROLE_TABLE = "table";

jest.mock("$lib/dataLoading.js", () => ({
  getSampleMetadata: jest.fn(() => Promise.resolve([{
    metadata: {
      qc: { name: "QC", value: "90", order: 7 },
      host_species: { name: "Host species", value: "Sciurus carolinensis", order: 2 }
    }
  }, {
    metadata: {
      host_species: { name: "Host species", value: "Ailuropoda melanoleuca", order: 2 },
      qc: { name: "QC", value: "40", order: 7 }
    }
  }]))
}));

it("isn't displayed if no batches are passed", () => {
  const { queryByRole } = render(SampleMetadataViewer);

  expect(queryByRole(ROLE_TABLE)).toBeNull();
});

it("displays resolved metadata w/ each row sorted by order", () => {
  const { getAllByRole } = render(SampleMetadataViewer, { batches: BATCHES });

  waitFor(() => {
    // Data rows + the header row
    expect(getAllByRole("row")).toHaveLength(METADATA.length + 1);
    const actualColumnHeaderContents = getAllByRole("columnheader")
      .map(({ textContent }) => textContent);
    expect(actualColumnHeaders).toEqual(["Host species", "QC"]);
    const actualTableCellContents = getAllByRole("cell")
      .map(({ textContent }) => textContent);
    expect(actualTableCellContents).toEqual([
      "Sciurus carolinensis", "90",
      "Ailuropoda melanoleuca", "40"
    ]);
  });
});

it("requests metadata w/ the correct arguments", () => {
  render(SampleMetadataViewer, { batches: BATCHES });

  waitFor(() => {
    expect(getSampleMetadata).toHaveBeenCalledWith({
      instKeyBatchDatePairs: BATCHES,
      numRows: 12
    });
  });
});

it("debounces the metadata request when batches change", async () => {
  jest.spyOn(debounceRef, "debounce");

  const { component } = render(SampleMetadataViewer, { batches: BATCHES });
  component.$set({ batches: ["some other batches"] });
  component.$set({ batches: BATCHES });

  waitFor(() => {
    expect(debounceRef.debounce).toHaveBeenCalledTimes(3);
  });
});
