import { fireEvent, render } from "@testing-library/svelte";
import UploadingPage from "./index.svelte";

it("is rendered w/ the data upload form", () => {
  const { container, getByRole } = render(UploadingPage);

  expect(container.querySelector("p").textContent)
    .toBe("Select or drag and drop your CSV files with sample metadata:");
  expect(getByRole("form")).toBeDefined();
});

it("shows the dialog on the upload success event", async () => {
  const DIALOG_TITLE = "Upload success";
  const ROLE_DIALOG = "dialog";

  const { getByRole, queryByRole } = render(UploadingPage);

  expect(queryByRole(ROLE_DIALOG, { name: DIALOG_TITLE }))
    .toBeNull();

  await fireEvent.submit(getByRole("form"));

  expect(queryByRole(ROLE_DIALOG, { name: DIALOG_TITLE }))
    .toBeDefined();
  expect(queryByRole("link", { name: "go to the dashboard" }))
    .toBeDefined();
});

