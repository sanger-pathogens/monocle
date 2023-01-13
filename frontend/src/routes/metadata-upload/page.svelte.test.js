import { fireEvent, render } from "@testing-library/svelte";
import { projectStore, userStore } from "../stores.js";
import MetadataUploadPage from "./+page.svelte";

const UPLOAD_URL = "some/upload/url";
const ROLE_FORM = "form";

projectStore.setFromResponse({
  upload_links: [{ label: "metadata", url: UPLOAD_URL }],
});

it("has the expected text", async () => {
  const { getByLabelText, getByRole, getByText } = render(MetadataUploadPage);

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(getByText("Metadata upload")).toBeDefined();
  expect(
    getByLabelText(
      "Select or drag and drop your CSV files (saved as UTF-8) with sample metadata:"
    )
  ).toBeDefined();
  expect(getByText("All metadata were successfully uploaded.")).toBeDefined();
});

it("has the expected upload URL", async () => {
  global.fetch = jest.fn(() => Promise.resolve());
  const { container, getByRole } = render(MetadataUploadPage);
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});

it("shows the app menu w/ the expected links", () => {
  userStore.setRole("admin");

  const { getByLabelText, queryByLabelText } = render(MetadataUploadPage);

  expect(getByLabelText("Download sample data")).toBeDefined();
  expect(queryByLabelText("Upload metadata")).toBeNull();
  expect(getByLabelText("Upload QC data")).toBeDefined();
  expect(getByLabelText("Upload in-silico data")).toBeDefined();
});
