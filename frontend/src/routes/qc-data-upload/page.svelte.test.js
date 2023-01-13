import { fireEvent, render } from "@testing-library/svelte";
import { projectStore, userStore } from "../stores.js";
import QCDataUploadPage from "./+page.svelte";

const UPLOAD_URL = "some/upload/url";
const ROLE_FORM = "form";

projectStore.setFromResponse({
  upload_links: [{ label: "qc data", url: UPLOAD_URL }],
});

it("has the expected text", async () => {
  const { getByLabelText, getByRole, getByText } = render(QCDataUploadPage);

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(getByText("QC data upload")).toBeDefined();
  expect(
    getByLabelText(
      "Select or drag and drop your files with tab-separated QC data:"
    )
  ).toBeDefined();
  expect(getByText("All QC data were successfully uploaded.")).toBeDefined();
});

it("accepts the expected file types", () => {
  const { container } = render(QCDataUploadPage);

  const fileInput = container.querySelector("form input");
  expect(fileInput.getAttribute("accept")).toBe(
    "text/plain,.txt,text/tab-separated-values,.tsv,.tab"
  );
});

it("has the expected upload URL", async () => {
  global.fetch = jest.fn(() => Promise.resolve());
  const { container, getByRole } = render(QCDataUploadPage);
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});

it("shows the app menu w/ the expected links", () => {
  userStore.setRole("admin");

  const { getByLabelText, queryByLabelText } = render(QCDataUploadPage);

  expect(getByLabelText("Download sample data")).toBeDefined();
  expect(getByLabelText("Upload metadata")).toBeDefined();
  expect(queryByLabelText("Upload QC data")).toBeNull();
  expect(getByLabelText("Upload in-silico data")).toBeDefined();
});
