import { act, fireEvent, render, waitFor } from "@testing-library/svelte";
import SampleMetadataViewer from "./_SampleMetadataViewer.svelte";
import debounce from "$lib/utils/debounce.js";
import { getSampleMetadata } from "$lib/dataLoading.js";

const BATCHES = ["some batches"];
const ROLE_BUTTON = "button";

// Spy on `debounce` w/o changing its implementation. (`jest.spyOn` couldn't be used, as it works only w/ objects.)
jest.mock("$lib/utils/debounce.js", () => {
  const originalDebounce = jest.requireActual("$lib/utils/debounce.js");
  return {
    __esModule: true,
    default: jest.fn(originalDebounce.default)
  };
});

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
  const { container } = render(SampleMetadataViewer);

  expect(container.innerHTML).toBe("");
});

it("displays resolved metadata w/ each row sorted by order", async () => {
  const { getAllByRole } = render(SampleMetadataViewer, { batches: BATCHES });

  await waitFor(() => {
    // Data rows + the header row
    expect(getAllByRole("row")).toHaveLength(3);
    const actualColumnHeaderContents = getAllByRole("columnheader")
      .map(({ textContent }) => textContent);
    expect(actualColumnHeaderContents).toEqual(["Host species", "QC"]);
    const actualTableCellContents = getAllByRole("cell")
      .map(({ textContent }) => textContent);
    expect(actualTableCellContents).toEqual([
      "Sciurus carolinensis", "90",
      "Ailuropoda melanoleuca", "40"
    ]);
  });
});

it("requests metadata w/ the correct arguments", async () => {
  render(SampleMetadataViewer, { batches: BATCHES });

  await waitFor(() => {
    expect(getSampleMetadata).toHaveBeenCalledWith({
      instKeyBatchDatePairs: BATCHES,
      numRows: 12,
      startRow: 1
    }, fetch);
  });
});

it("debounces the metadata request when batches change", async () => {
  debounce.mockClear();
  const { component } = render(SampleMetadataViewer, { batches: BATCHES });
  await act(() => {
    component.$set({ batches: ["some other batches"] });
  });
  await act(() => {
    component.$set({ batches: BATCHES });
  });

  expect(debounce).toHaveBeenCalledTimes(3);
});

describe("pagination", () => {
  const LABEL_FIRST_BUTTON = "First page";
  const LABEL_NEXT_BUTTON = "Next page";
  const LABEL_PREV_BUTTON = "Previous page";
  const LABEL_LOADING_INDICATOR = "please wait";
  const NUM_METADATA_ROWS_PER_PAGE = 12;

  beforeEach(() => {
    getSampleMetadata.mockClear();
  });

  it("disables First and Previous buttons only if the first page is shown", async () => {
    const { getByRole } = render(SampleMetadataViewer, { batches: BATCHES });

    expect(getByRole(ROLE_BUTTON, { name: LABEL_FIRST_BUTTON }).disabled)
      .toBeTruthy();
    expect(getByRole(ROLE_BUTTON, { name: LABEL_PREV_BUTTON }).disabled)
      .toBeTruthy();

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }));

    expect(getByRole(ROLE_BUTTON, { name: LABEL_FIRST_BUTTON }).disabled)
      .toBeFalsy();
    expect(getByRole(ROLE_BUTTON, { name: LABEL_PREV_BUTTON }).disabled)
      .toBeFalsy();
  });

  it("disables Next button only if the last page is shown", async () => {
    const { getByRole } = render(SampleMetadataViewer, { batches: BATCHES });

    expect(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }).disabled)
      .toBeFalsy();

    getSampleMetadata.mockResolvedValueOnce({ "last row": 99, "total rows": 99 });
    fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }));

    await waitFor(() => {
      expect(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }).disabled)
        .toBeTruthy();
    });
  });

  it("requests and loads the next page when Next button is clicked", async () => {
    jest.useFakeTimers();
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, { batches: BATCHES });
    getSampleMetadata.mockClear();

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }));

    expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
    jest.runAllTimers();
    expect(getSampleMetadata).toHaveBeenCalledTimes(1);
    const expectedStartRow = NUM_METADATA_ROWS_PER_PAGE + 1;
    expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(expectedStartRow);
    jest.useRealTimers();
  });

  it("requests and loads the previous page when Previous button is clicked", async () => {
    jest.useFakeTimers();
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, { batches: BATCHES });
    const nextBtn = getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);
    getSampleMetadata.mockClear();

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_PREV_BUTTON }));

    expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
    jest.runAllTimers();
    expect(getSampleMetadata).toHaveBeenCalledTimes(1);
    const expectedStartRow = NUM_METADATA_ROWS_PER_PAGE + 1;
    expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(expectedStartRow);
    jest.useRealTimers();
  });

  it("requests and loads the first page when First button is clicked", async () => {
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, { batches: BATCHES });
    const nextBtn = getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);

    fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_FIRST_BUTTON }));

    await waitFor(() => {
      expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
      expect(getSampleMetadata).toHaveBeenCalledTimes(1);
      expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(1);
    });
  });
});
