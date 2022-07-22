import { fireEvent, render } from "@testing-library/svelte";
import { writable } from "svelte/store";
import DataUploadPage from "./TestDataUploadPage.svelte";

const DATA_TYPE = "data";
const UPLOAD_URL = "some/upload/url";
const PROJECT = {
  project: { upload_links: [{ label: DATA_TYPE, url: UPLOAD_URL }] },
};
const ROLE_FORM = "form";

it("renders the expected slots", async () => {
  const { getByLabelText, getByRole, getByText } = render(DataUploadPage, {
    dataType: DATA_TYPE,
    session: writable(PROJECT),
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(getByText("Data upload")).toBeDefined();
  expect(getByLabelText("Select or drag and drop your files:")).toBeDefined();
  expect(getByText("All files were successfully uploaded.")).toBeDefined();
});

it("can accept only specified file extensions", () => {
  const fileTypes = ".csv,.txt";

  const { container } = render(DataUploadPage, {
    dataType: DATA_TYPE,
    fileTypes,
    session: writable(PROJECT),
  });

  const fileInput = container.querySelector("form input");
  expect(fileInput.getAttribute("accept")).toBe(fileTypes);
});

it("shows the dialog on the upload success event", async () => {
  const DIALOG_TITLE = "Upload success";
  const ROLE_DIALOG = "dialog";

  const { getByRole, queryByRole } = render(DataUploadPage, {
    dataType: DATA_TYPE,
    session: writable(PROJECT),
  });

  expect(queryByRole(ROLE_DIALOG, { name: DIALOG_TITLE })).toBeNull();

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(getByRole(ROLE_DIALOG)).toBeDefined();
  expect(getByRole("heading", { name: DIALOG_TITLE })).toBeDefined();
  expect(getByRole("link", { name: "go to the dashboard" })).toBeDefined();
});
