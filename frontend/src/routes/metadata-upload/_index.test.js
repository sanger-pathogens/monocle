import { fireEvent, render } from "@testing-library/svelte";
import MetadataUploadPage from "./index.svelte";
import { writable } from "svelte/store";

const UPLOAD_URL = "some/upload/url";
const PROJECT = {
  project: { upload_links: [{ label: "metadata", url: UPLOAD_URL }] },
};
const ROLE_FORM = "form";

it("has the expected text", async () => {
  const { getByLabelText, getByRole, getByText } = render(MetadataUploadPage, {
    session: writable(PROJECT),
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
    session: writable(PROJECT),
  });
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});
