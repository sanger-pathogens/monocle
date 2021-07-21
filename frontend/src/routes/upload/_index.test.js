import { fireEvent, render } from "@testing-library/svelte";
import UploadingPage from "./index.svelte";

it("renders the metadata uploading component", () => {
  const { getByRole, getByText } = render(UploadingPage);

  expect(getByText("Select or drag and drop your Excel files with sample metadata:"))
    .toBeDefined();
  expect(getByRole("button", { name: "Upload" }))
    .toBeDefined();
});

it("shows the dialog on the upload success event", async () => {
  const DIALOG_TITLE = "Upload success";
  const ROLE_DIALOG = "dialog";

  const { container, queryByRole } = render(UploadingPage);

  expect(queryByRole(ROLE_DIALOG, { name: DIALOG_TITLE }))
    .toBeNull();

  await fireEvent.submit(container.querySelector("form"));

  expect(queryByRole(ROLE_DIALOG, { name: DIALOG_TITLE }))
    .toBeDefined();
  expect(queryByRole("link", { name: "go to dashboard" }))
    .toBeDefined();
});

