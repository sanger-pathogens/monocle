import { fireEvent, render } from "@testing-library/svelte";
import { projectStore, userStore } from "../_stores.js";
import InSilicoUploadPage from "./+page.svelte";

const UPLOAD_URL = "some/upload/url";
const ROLE_FORM = "form";

projectStore.setFromResponse({
  upload_links: [{ label: "in silico", url: UPLOAD_URL }],
});

it("has the expected text", async () => {
  const { container, getByRole } = render(InSilicoUploadPage);

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(container.querySelector("h2").textContent).toBe(
    "In silico data upload"
  );
  expect(container.querySelector("p").textContent).toBe(
    "Select or drag and drop your files with tab-separated in silico data:"
  );
  expect(container.querySelector("[role=dialog] p").textContent).toBe(
    "All in silico data were successfully uploaded."
  );
});

it("accepts the expected file types", () => {
  const { container } = render(InSilicoUploadPage);

  const fileInput = container.querySelector("form input");
  expect(fileInput.getAttribute("accept")).toBe(
    "text/plain,.txt,text/tab-separated-values,.tsv,.tab"
  );
});

it("has the expected upload URL", async () => {
  global.fetch = jest.fn(() => Promise.resolve());
  const { container, getByRole } = render(InSilicoUploadPage);
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});

it("shows the app menu w/ the expected links", () => {
  userStore.setRole("admin");

  const { getByLabelText, queryByLabelText } = render(InSilicoUploadPage);

  expect(getByLabelText("View and download sample data")).toBeDefined();
  expect(getByLabelText("Upload metadata")).toBeDefined();
  expect(getByLabelText("Upload QC data")).toBeDefined();
  expect(queryByLabelText("Upload in-silico data")).toBeNull();
});
