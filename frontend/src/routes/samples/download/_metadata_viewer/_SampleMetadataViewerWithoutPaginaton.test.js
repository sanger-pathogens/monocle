import { render } from "@testing-library/svelte";
import SimpleSampleMetadataViewer from "./_SampleMetadataViewerWithoutPaginaton.svelte";

it("displayes passed metadata in a table", () => {
  const metadata = [{
    metadata: [{ name: "Sample ID", value: "1a" }, { name: "Country", value: "UK" }]
  }, {
    metadata: [{ name: "Sample ID", value: "2b" }, { name: "Country", value: "UA" }]
  }];

  const { getAllByRole, getByRole } = render(SimpleSampleMetadataViewer, { metadata });

  expect(getByRole("table")).toBeDefined();
  // Data rows + the header row
  expect(getAllByRole("row")).toHaveLength(metadata.length + 1);
  metadata[0].metadata.forEach(({ name }) => {
    expect(getByRole("columnheader", { name })).toBeDefined();
  });
  const roleTableCell = "cell";
  metadata.forEach(({ metadata: sampleMetadata }) => {
    sampleMetadata.forEach(({ value }) => {
      expect(getByRole(roleTableCell, { name: value })).toBeDefined();
    });
  });
});
