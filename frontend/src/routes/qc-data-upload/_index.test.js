import { fireEvent, render } from "@testing-library/svelte";
import QCDataUploadPage from "./index.svelte";
import { writable } from "svelte/store";

const UPLOAD_URL = "some/upload/url";
const PROJECT = {
  project: { upload_links: [{ label: "qc data", url: UPLOAD_URL }] },
};
const ROLE_FORM = "form";

it("has the expected text", async () => {
  const { getByLabelText, getByRole, getByText } = render(QCDataUploadPage, {
    session: writable(PROJECT),
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(getByText("QC data upload")).toBeDefined();
  expect(
    getByLabelText(
      "Select or drag and drop your CSV files (saved as UTF-8) with sample QC data:"
    )
  ).toBeDefined();
  expect(getByText("All QC data were successfully uploaded.")).toBeDefined();
});

it("has the expected upload URL", async () => {
  global.fetch = jest.fn(() => Promise.resolve());
  const { container, getByRole } = render(QCDataUploadPage, {
    session: writable(PROJECT),
  });
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});
