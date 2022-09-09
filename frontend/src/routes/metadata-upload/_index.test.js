import { fireEvent, render } from "@testing-library/svelte";
import MetadataUploadPage from "./index.svelte";
import { writable } from "svelte/store";

const UPLOAD_URL = "some/upload/url";
const SESSION_STATE = {
  project: { upload_links: [{ label: "metadata", url: UPLOAD_URL }] },
  user: { role: "admin" },
};
const ROLE_FORM = "form";

it("has the expected text", async () => {
  const { getByLabelText, getByRole, getByText } = render(MetadataUploadPage, {
    session: writable(SESSION_STATE),
  });

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
  const { container, getByRole } = render(MetadataUploadPage, {
    session: writable(SESSION_STATE),
  });
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});

it("shows the app menu w/ the expected links", () => {
  const { getByLabelText, queryByLabelText } = render(MetadataUploadPage, {
    session: writable(SESSION_STATE),
  });

  expect(getByLabelText("View and download sample data")).toBeDefined();
  expect(queryByLabelText("Upload metadata")).toBeNull();
  expect(getByLabelText("Upload QC data")).toBeDefined();
  expect(getByLabelText("Upload in-silico data")).toBeDefined();
});
