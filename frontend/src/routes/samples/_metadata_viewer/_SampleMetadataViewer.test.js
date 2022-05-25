import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { get } from "svelte/store";
import debounce from "$lib/utils/debounce.js";
import { getSampleMetadata } from "$lib/dataLoading.js";
import {
  columnsStore,
  columnsToDisplayStore,
  distinctColumnValuesStore,
  filterStore,
} from "../_stores.js";
import SampleMetadataViewer from "./_SampleMetadataViewer.svelte";

const BATCHES = ["some batches"];
const ROLE_BUTTON = "button";

// Spy on `debounce` w/o changing its implementation. (`jest.spyOn` couldn't be used, as it works only w/ objects.)
jest.mock("$lib/utils/debounce.js", () => {
  const originalDebounce = jest.requireActual("$lib/utils/debounce.js");
  return {
    __esModule: true,
    default: jest.fn(originalDebounce.default),
  };
});

jest.mock("$lib/dataLoading.js", () => ({
  getSampleMetadata: jest.fn(() =>
    Promise.resolve({
      "total rows": 4,
      "last row": 4,
      samples: [
        {
          metadata: {
            qc: { title: "QC", value: "90", order: 7 },
            host_species: {
              title: "Host species",
              value: "Sciurus carolinensis",
              order: 2,
            },
          },
          "in silico": {
            ST: { title: "ST", value: "some value", order: 1 },
          },
        },
        {
          metadata: {
            host_species: {
              title: "Host species",
              value: "Ailuropoda melanoleuca",
              order: 2,
            },
            qc: { title: "QC", value: "40", order: 7 },
          },
          "in silico": {
            ST: { title: "ST", value: "another value", order: 1 },
          },
        },
      ],
    })
  ),
}));

it("isn't displayed if no batches are passed", () => {
  const { container } = render(SampleMetadataViewer);

  expect(container.innerHTML).toBe("<div></div>");
});

it("displays resolved metadata w/ each row sorted by order", async () => {
  const { getAllByRole } = render(SampleMetadataViewer, { batches: BATCHES });

  const expectedColumnHeaders = ["Host species", "QC", "ST"];
  await waitFor(() => {
    // Data rows + the header row
    expect(getAllByRole("row")).toHaveLength(3);
    getAllByRole("columnheader").forEach(({ textContent }, i) =>
      expect(textContent.startsWith(expectedColumnHeaders[i])).toBeTruthy()
    );
    const actualTableCellContents = getAllByRole("cell").map(
      ({ textContent }) => textContent
    );
    expect(actualTableCellContents).toEqual([
      "Sciurus carolinensis",
      "90",
      "some value",
      "Ailuropoda melanoleuca",
      "40",
      "another value",
    ]);
  });
});

it("requests metadata w/ the correct arguments", async () => {
  render(SampleMetadataViewer, { batches: BATCHES });

  await waitFor(() => {
    expect(getSampleMetadata).toHaveBeenCalledWith(
      {
        instKeyBatchDatePairs: BATCHES,
        filter: {
          filterState: get(filterStore),
          distinctColumnValuesState: get(distinctColumnValuesStore),
        },
        numRows: 17,
        startRow: 1,
      },
      fetch
    );
  });
});

it("requests metadata if selected columns change", async () => {
  getSampleMetadata.mockClear();
  render(SampleMetadataViewer, { batches: BATCHES });

  await waitFor(() => {
    expect(getSampleMetadata).toHaveBeenCalledTimes(1);
  });

  getSampleMetadata.mockClear();
  columnsStore.set({ metadata: [] });

  await waitFor(() => {
    expect(getSampleMetadata).toHaveBeenCalledTimes(1);
    expect(getSampleMetadata).toHaveBeenCalledWith(
      {
        instKeyBatchDatePairs: BATCHES,
        filter: {
          filterState: get(filterStore),
          distinctColumnValuesState: get(distinctColumnValuesStore),
        },
        columns: get(columnsToDisplayStore),
        numRows: 17,
        startRow: 1,
      },
      fetch
    );
  });
});

it("debounces the metadata request when batches change", async () => {
  debounce.mockClear();
  const { component } = render(SampleMetadataViewer, { batches: BATCHES });
  await component.$set({ batches: ["some other batches"] });
  await component.$set({ batches: BATCHES });

  expect(debounce).toHaveBeenCalledTimes(3);
});

describe("pagination", () => {
  const LABEL_FIRST_BUTTON = "First page";
  const LABEL_NEXT_BUTTON = "Next page";
  const LABEL_PREV_BUTTON = "Previous page";
  const LABEL_LOADING_INDICATOR = "please wait";
  const NUM_SAMPLES_PER_PAGE = 17;

  beforeEach(() => {
    getSampleMetadata.mockClear();
  });

  it("displays two pagination navigations", async () => {
    const { getAllByRole } = render(SampleMetadataViewer, { batches: BATCHES });

    await waitFor(() => {
      expect(
        getAllByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }).length
      ).toBe(2);
    });
  });

  it("requests and loads the next page when Next button is clicked", async () => {
    jest.useFakeTimers();
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, {
      batches: BATCHES,
    });
    getSampleMetadata.mockClear();

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }));

    expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
    jest.runAllTimers();
    expect(getSampleMetadata).toHaveBeenCalledTimes(1);
    const expectedStartRow = NUM_SAMPLES_PER_PAGE + 1;
    expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(expectedStartRow);
    jest.useRealTimers();
  });

  it("requests and loads the previous page when Previous button is clicked", async () => {
    jest.useFakeTimers();
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, {
      batches: BATCHES,
    });
    const nextBtn = getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);
    getSampleMetadata.mockClear();

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_PREV_BUTTON }));

    expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
    jest.runAllTimers();
    expect(getSampleMetadata).toHaveBeenCalledTimes(1);
    const expectedStartRow = NUM_SAMPLES_PER_PAGE + 1;
    expect(getSampleMetadata.mock.calls[0][0].startRow).toBe(expectedStartRow);
    jest.useRealTimers();
  });

  it("requests and loads the first page when First button is clicked", async () => {
    const { getByLabelText, getByRole } = render(SampleMetadataViewer, {
      batches: BATCHES,
    });
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
