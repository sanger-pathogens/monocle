import { fireEvent, render, waitFor } from "@testing-library/svelte";
import SampleMetadataViewer from "./_SampleMetadataViewer.svelte";
import debounce from "$lib/utils/debounce.js"
import { getSampleMetadata } from "$lib/dataLoading.js";

// A workaround for Jest's `spyOn` working only for object methods.
const debounceRef = { debounce };

const BATCHES = ["some batches"];
const ROLE_BUTTON = "button";
const ROLE_TABLE = "table";

jest.mock("$lib/dataLoading.js", () => ({
  getSampleMetadata: jest.fn(() => Promise.resolve({
    "total rows": 4,
    "last row": 4,
    samples: [{
      metadata: {
        qc: { name: "QC", value: "90", order: 7 },
        host_species: { name: "Host species", value: "Sciurus carolinensis", order: 2 }
      }
    }, {
      metadata: {
        host_species: { name: "Host species", value: "Ailuropoda melanoleuca", order: 2 },
        qc: { name: "QC", value: "40", order: 7 }
      }
  }] }))
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
      numRows: 12,
      startRow: 1
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

describe("pagination", () => {
  const BUTTON_NAME_FIRST = "First";
  const BUTTON_NAME_NEXT = "Next";
  const BUTTON_NAME_PREV = "Previous";
  const LABEL_LOADING_INDICATOR = "please wait";
  const NUM_METADATA_ROWS_PER_PAGE = 12;

  it("disables First and Previous buttons only if the first page is shown", async () => {
    const { getByRole } = render(SampleMetadataViewer, { batches: BATCHES });

    expect(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_FIRST }).disabled)
      .toBeTruthy();
    expect(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_PREV }).disabled)
      .toBeTruthy();

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT }));

    expect(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_FIRST }).disabled)
      .toBeFalsy();
    expect(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_PREV }).disabled)
      .toBeFalsy();
  });

  it("disables Next button only if the last page is shown", async () => {
    const { getByRole } = render(SampleMetadataViewer, { batches: BATCHES });

    expect(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT }).disabled)
      .toBeFalsy();

    getSampleMetadata.mockResolvedValueOnce({ "last row": 99, "total rows": 99 });
    fireEvent.click(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT }));

    waitFor(() => {
      expect(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT }).disabled)
        .toBeTruthy();
    });
  });

  it("requests and loads the next page when Next button is clicked", async () => {
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, { batches: BATCHES });

    fireEvent.click(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT }));

    waitFor(() => {
      expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
      expect(getSampleMetadata).toHaveBeenCalledTimes(1);
      const expectedStartRow = NUM_METADATA_ROWS_PER_PAGE + 1;
      expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(expectedStartRow);
    });
  });

  it("requests and loads the previous page when Previous button is clicked", async () => {
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, { batches: BATCHES });
    const nextBtn = getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);

    fireEvent.click(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_PREV }));

    waitFor(() => {
      expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
      expect(getSampleMetadata).toHaveBeenCalledTimes(1);
      const expectedStartRow = NUM_METADATA_ROWS_PER_PAGE + 1;
      expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(expectedStartRow);
    });
  });

  it("requests and loads the first page when First button is clicked", async () => {
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, { batches: BATCHES });
    const nextBtn = getByRole(ROLE_BUTTON, { name: BUTTON_NAME_NEXT });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);

    fireEvent.click(getByRole(ROLE_BUTTON, { name: BUTTON_NAME_FIRST }));

    waitFor(() => {
      expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
      expect(getSampleMetadata).toHaveBeenCalledTimes(1);
      expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(1);
    });
  });
});
