import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { get } from "svelte/store";
import { getSampleMetadata } from "$lib/dataLoading.js";
import { distinctColumnValuesStore, filterStore } from "./_stores.js";
import MetadataDownloadButton from "./_MetadataDownloadButton.svelte";

const BATCHES = ["fake batches"];
const DOWNLOAD_URL = "some/url";
const LABEL_METADATA_DOWNLOAD_BUTTON = "Download metadata";
const ROLE_BUTTON = "button";

jest.mock("$lib/dataLoading.js", () => ({
  getSampleMetadata: jest.fn(() => Promise.resolve())
}));

global.URL.createObjectURL = () => DOWNLOAD_URL;
global.URL.revokeObjectURL = () => {};

it("requests metadata CSV on click", async () => {
  const { getByRole } = render(MetadataDownloadButton, { batches: BATCHES});

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON }));

  expect(getSampleMetadata).toHaveBeenCalledTimes(1);
  expect(getSampleMetadata).toHaveBeenCalledWith(
    { asCsv: true,
      instKeyBatchDatePairs: BATCHES,
      filter: { filterState: get(filterStore), distinctColumnValuesState: get(distinctColumnValuesStore) }
    },
    fetch);
});

it("requests metadata CSV on click passing filter and distinct value state from props", async () => {
  const filterState = "fake filter state";
  const distinctColumnValuesState = "fake distinct value state";
  const { getByRole } = render(MetadataDownloadButton, {
    batches: BATCHES,
    filterState,
    distinctColumnValuesState
  });

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON }));

  expect(getSampleMetadata).toHaveBeenCalledWith(
    { asCsv: true,
      instKeyBatchDatePairs: BATCHES,
      filter: { filterState, distinctColumnValuesState }
    },
    fetch);
});

it("is disabled and shows the loading text while waiting for the metadata CSV", async () => {
  const { getByRole } = render(MetadataDownloadButton, { batches: BATCHES });

  const metadataDownloadButton = getByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON });
  await fireEvent.click(metadataDownloadButton);

  expect(metadataDownloadButton.disabled).toBeTruthy();
  expect(getByRole(ROLE_BUTTON, { name: "Preparing download" }))
    .toBeDefined();
});

it("hides the loading state, frees resources, and downloads metadata CSV once it's prepared", async () => {
  const fileNameWithoutExtension = "file-name";
  const hiddenDownloadLink = document.createElement("a");
  hiddenDownloadLink.click = jest.fn();
  const createAnchorElement = () => hiddenDownloadLink;
  const { getByRole } = render(MetadataDownloadButton, {
    batches: BATCHES,
    fileNameWithoutExtension,
    injectedCreateAnchorElement: createAnchorElement
  });
  global.URL.revokeObjectURL = jest.fn();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON }));

  await waitFor(() => {
    expect(hiddenDownloadLink.click).toHaveBeenCalledTimes(1);
    expect(hiddenDownloadLink.href).toBe(`${global.location.href}${DOWNLOAD_URL}`);
    expect(hiddenDownloadLink.download).toBe(`${fileNameWithoutExtension}.csv`);
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
  const { getByRole } = render(MetadataDownloadButton, {
    batches: BATCHES,
    injectedCreateAnchorElement: createAnchorElement
  });
  global.URL.revokeObjectURL = jest.fn();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_METADATA_DOWNLOAD_BUTTON }));

  await waitFor(() => {
    expect(URL.revokeObjectURL).toHaveBeenCalledWith(DOWNLOAD_URL);
    expect(hiddenDownloadLink.parentElement).toBeNull();
  });
});
