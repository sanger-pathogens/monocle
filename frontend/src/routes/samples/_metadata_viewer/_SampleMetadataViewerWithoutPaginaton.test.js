import { render, waitFor } from "@testing-library/svelte";
import SimpleSampleMetadataViewer from "./_SampleMetadataViewerWithoutPaginaton.svelte";

const LABEL_LOADING_INDICATOR = "please wait";
const ROLE_COLUMN_HEADER = "columnheader";
const ROLE_TABLE = "table";
const ROLE_TABLE_CELL = "cell";

it("isn't displayed if a metadata promise isn't passed", () => {
  const { queryByRole } = render(SimpleSampleMetadataViewer);

  expect(queryByRole(ROLE_TABLE)).toBeNull();
});

it("shows the loading indicator if the metadata promise is pending", () => {
  const { getByLabelText } = render(SimpleSampleMetadataViewer,
    { metadataPromise: new Promise(() => {})});

  expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
});

describe("on metadata resolved", () => {
  const METADATA = [{
    metadata: [{ name: "Sample ID", value: "1a" }, { name: "Country", value: "UK" }]
  }, {
    metadata: [{ name: "Sample ID", value: "2b" }, { name: "Country", value: "UA" }]
  }];

  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(SimpleSampleMetadataViewer,
      { metadataPromise: Promise.resolve(METADATA) });

    await waitFor(() => {
      expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
    });
  });

  it("displays metadata in a table", async () => {
    const { getByRole } = render(SimpleSampleMetadataViewer,
      { metadataPromise: Promise.resolve(METADATA) });

    await waitFor(() => {
      expectMetadataToBeShown(getByRole);
    });
  });

  it("shows the loading indicator and keeps showing old metadata while new metadata is loading", async () => {
    const { component, findByRole, getByRole, getByLabelText } =
      render(SimpleSampleMetadataViewer, { metadataPromise: Promise.resolve(METADATA) });

    await findByRole(ROLE_TABLE_CELL, { name: METADATA[0].metadata[0].value });

    const endlessPromise = new Promise(() => {});
    component.$set({ metadataPromise: endlessPromise });

    await waitFor(() => {
      expect(getByLabelText(LABEL_LOADING_INDICATOR)).toBeDefined();
      expectMetadataToBeShown(getByRole);
    });
  });

  function expectMetadataToBeShown(getByRole) {
    expect(getByRole(ROLE_TABLE)).toBeDefined();
    METADATA[0].metadata.forEach(({ name }) => {
      expect(getByRole(ROLE_COLUMN_HEADER, { name })).toBeDefined();
    });
    METADATA.forEach(({ metadata: sampleMetadata }) => {
      sampleMetadata.forEach(({ value }) => {
        expect(getByRole(ROLE_TABLE_CELL, { name: value })).toBeDefined();
      });
    });
  }

  it("displays a message if there's no metadata", async () => {
    const { getByRole, queryByLabelText } = render(SimpleSampleMetadataViewer,
      { metadataPromise: Promise.resolve([]) });

    await waitFor(() => {
      expect(getByRole(ROLE_TABLE_CELL, { name: "No data. Try to refresh or change a filter." }))
        .toBeDefined();
      expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
    });
  });
});

describe("on error", () => {
  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(SimpleSampleMetadataViewer,
      { metadataPromise: Promise.reject() });

    await waitFor(() => {
      expect(queryByLabelText(LABEL_LOADING_INDICATOR)).toBeNull();
    });
  });

  it("displays the error", async () => {
    const { findByText } = render(SimpleSampleMetadataViewer,
      { metadataPromise: Promise.reject() });

    const errorElement = await findByText(/^Error while fetching metadata/);
    expect(errorElement).toBeDefined();
  });
});