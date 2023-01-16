import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { get } from "svelte/store";
import {
  DATA_TYPE_METADATA,
  DATA_TYPE_QC,
  DATA_TYPE_IN_SILICO,
} from "$lib/constants.js";
import {
  // The following import is needed for the mock to work.
  // eslint-disable-next-line no-unused-vars
  getDistinctColumnValues,
} from "$lib/dataLoading.js";
import SimpleSampleMetadataViewer from "./SampleMetadataViewerWithoutPaginaton.svelte";
import {
  columnsStore,
  distinctColumnValuesStore,
  filterStore,
} from "../../stores.js";

jest.mock("$lib/dataLoading.js", () => ({
  getDistinctColumnValues: jest.fn(() => Promise.resolve([])),
}));

const BATCHES = [];
const LABEL_LOADING_INDICATOR = "please wait";
const ROLE_COLUMN_HEADER = "columnheader";
const ROLE_TABLE = "table";
const ROLE_TABLE_CELL = "cell";

it("isn't displayed if a metadata promise isn't passed", () => {
  const { queryByRole } = render(SimpleSampleMetadataViewer, {
    batches: BATCHES,
  });

  expect(queryByRole(ROLE_TABLE)).toBeNull();
});

it("shows the loading indicator if the metadata promise is pending", () => {
  const { getByLabelText } = render(SimpleSampleMetadataViewer, {
    metadataPromise: new Promise(() => {}),
    batches: BATCHES,
  });

  expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
});

describe("on metadata resolved", () => {
  const EMPTY_VALUE = "";
  const METADATA = [
    [
      {
        title: "Sample ID",
        name: "sample_id",
        value: "1a",
        dataType: DATA_TYPE_METADATA,
      },
      { title: "E", name: "e", value: 9, dataType: DATA_TYPE_QC },
      { title: "ST", name: "st", value: "v1", dataType: DATA_TYPE_IN_SILICO },
    ],
    [
      {
        title: "Sample ID",
        name: "sample_id",
        value: "1b",
        dataType: DATA_TYPE_METADATA,
      },
      { title: "E", name: "e", value: 42, dataType: DATA_TYPE_QC },
      { title: "ST", name: "st", value: null, dataType: DATA_TYPE_IN_SILICO },
    ],
  ];

  columnsStore.set({
    metadata: [
      {
        name: "Category A",
        columns: [
          { displayName: "Sample ID", name: "sample_id", selected: true },
          { displayName: "This one isn't selected", name: "xyz" },
        ],
      },
    ],
    "qc data": [
      {
        name: "Category B",
        columns: [{ displayName: "E", name: "e", selected: true }],
      },
    ],
    "in silico": [
      {
        name: "Category C",
        columns: [{ displayName: "ST", name: "st", selected: true }],
      },
    ],
  });

  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(SimpleSampleMetadataViewer, {
      metadataPromise: Promise.resolve(METADATA),
      batches: BATCHES,
    });

    await waitFor(() => {
      expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
    });
  });

  it("displays metadata in a table", async () => {
    const { getByRole } = render(SimpleSampleMetadataViewer, {
      metadataPromise: Promise.resolve(METADATA),
      batches: BATCHES,
    });

    await waitFor(() => {
      expectMetadataToBeShown(getByRole);
    });
  });

  it("shows the loading indicator and keeps showing old metadata while new metadata is loading", async () => {
    const { component, findByRole, getByRole, getByLabelText } = render(
      SimpleSampleMetadataViewer,
      { metadataPromise: Promise.resolve(METADATA), batches: BATCHES }
    );

    await findByRole(ROLE_TABLE_CELL, { name: METADATA[0][0].value });

    const endlessPromise = new Promise(() => {});
    component.$set({ metadataPromise: endlessPromise });

    await waitFor(() => {
      expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
      expectMetadataToBeShown(getByRole);
    });
  });

  it("displays a message if there's no metadata", async () => {
    const { getByRole, queryByLabelText } = render(SimpleSampleMetadataViewer, {
      metadataPromise: Promise.resolve([]),
      batches: BATCHES,
    });

    await waitFor(() => {
      expect(
        getByRole(ROLE_TABLE_CELL, {
          name: "No samples found. Try different batches or filters.",
        })
      ).toBeDefined();
      expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
    });
  });

  it("resets distinct column values if batches change", async () => {
    const { component } = render(SimpleSampleMetadataViewer, {
      metadataPromise: Promise.resolve([]),
      batches: BATCHES,
    });
    distinctColumnValuesStore.updateFromDistinctValuesResponse([
      {
        "field type": "metadata",
        fields: [
          {
            name: "column name",
            matches: [{ number: 9, value: "some value" }],
          },
        ],
      },
    ]);

    await component.$set({ batches: ["something"] });

    expect(get(distinctColumnValuesStore)).toEqual({
      metadata: {},
      "in silico": {},
      "qc data": {},
    });
  });

  describe("filter column button", () => {
    it("is displayed for each column", async () => {
      const { getByLabelText } = render(SimpleSampleMetadataViewer, {
        metadataPromise: Promise.resolve(METADATA),
        batches: BATCHES,
      });

      await waitFor(() => {
        METADATA[0].forEach(({ title }) => {
          expect(
            getByLabelText(`Toggle the filter menu for column ${title}`)
          ).toBeDefined();
        });
      });
    });

    it("toggles a filter for a corresponding column", async () => {
      const { findByLabelText, getByLabelText, queryByLabelText } = render(
        SimpleSampleMetadataViewer,
        { metadataPromise: Promise.resolve(METADATA), batches: BATCHES }
      );
      const columnTitle = METADATA[0][0].title;
      const filterButton = await findByLabelText(
        `Toggle the filter menu for column ${columnTitle}`
      );

      let filterDialogLabel = /^Filter samples by .+$/;
      expect(queryByLabelText(filterDialogLabel)).toBeNull();

      await fireEvent.click(filterButton);

      filterDialogLabel = `Filter samples by ${columnTitle}`;
      expect(getByLabelText(filterDialogLabel)).toBeDefined();

      await fireEvent.click(filterButton);

      expect(queryByLabelText(filterDialogLabel)).toBeNull();
    });

    it("closes an open filter before opening a filter for another column", async () => {
      const { findByLabelText, getByLabelText, queryByLabelText } = render(
        SimpleSampleMetadataViewer,
        { metadataPromise: Promise.resolve(METADATA), batches: BATCHES }
      );

      const columnTitle = METADATA[0][0].title;
      const filterButton = await findByLabelText(
        `Toggle the filter menu for column ${columnTitle}`
      );
      await fireEvent.click(filterButton);

      const filterDialogLabel = `Filter samples by ${columnTitle}`;
      expect(getByLabelText(filterDialogLabel)).toBeDefined();

      const anotherColumnTitle = METADATA[0][1].title;
      await fireEvent.click(
        getByLabelText(
          `Toggle the filter menu for column ${anotherColumnTitle}`
        )
      );

      expect(queryByLabelText(filterDialogLabel)).toBeNull();
      expect(
        getByLabelText(`Filter samples by ${anotherColumnTitle}`)
      ).toBeDefined();
    });

    it("has a different color for an active filter", async () => {
      const columnOfActiveFilter = METADATA[0][0];
      filterStore.update((filterState) => {
        filterState.metadata[columnOfActiveFilter.name] = {};
        return filterState;
      });
      const { findByRole, getByRole } = render(SimpleSampleMetadataViewer, {
        metadataPromise: Promise.resolve(METADATA),
        batches: BATCHES,
      });

      const columnHeaderElementOfActiveFilter = await findByRole(
        "columnheader",
        { name: new RegExp(`^${columnOfActiveFilter.title}`) }
      );
      const activeFilterButtonColor = columnHeaderElementOfActiveFilter
        .querySelector("svg")
        .getAttribute("fill");
      const filterButtonColor = getByRole("columnheader", {
        name: new RegExp(`^${METADATA[0][1].title}`),
      })
        .querySelector("svg")
        .getAttribute("fill");
      expect(activeFilterButtonColor).not.toBe(filterButtonColor);
    });
  });

  function expectMetadataToBeShown(getByRole) {
    expect(getByRole(ROLE_TABLE)).toBeDefined();
    METADATA[0].forEach(({ title }) => {
      expect(getByRole(ROLE_COLUMN_HEADER, { name: title })).toBeDefined();
    });
    METADATA.forEach((sampleMetadata) => {
      sampleMetadata.forEach(({ value }) => {
        expect(
          getByRole(ROLE_TABLE_CELL, {
            name: value === null ? EMPTY_VALUE : value,
          })
        ).toBeDefined();
      });
    });
  }
});

describe("on error", () => {
  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(SimpleSampleMetadataViewer, {
      metadataPromise: Promise.reject(),
      batches: BATCHES,
    });

    await waitFor(() => {
      expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
    });
  });

  it("displays the error", async () => {
    const { findByText } = render(SimpleSampleMetadataViewer, {
      metadataPromise: Promise.reject(),
      batches: BATCHES,
    });

    const errorElement = await findByText(
      /^An error occured while fetching metadata/
    );
    expect(errorElement).toBeDefined();
  });
});
