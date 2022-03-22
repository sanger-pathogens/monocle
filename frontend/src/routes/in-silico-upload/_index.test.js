import { fireEvent, render } from "@testing-library/svelte";
import UploadingPage from "./index.svelte";

it("is rendered w/ the data upload form that accepts only specified file extensions", () => {
  const { container } = render(UploadingPage);

  expect(container.querySelector("p").textContent)
    .toBe("Select or drag and drop your files with tab-separated in silico data:");
  const fileInput = container.querySelector("form input");
  expect(fileInput.getAttribute("accept"))
    .toBe("text/plain,.txt,text/tab-separated-values,.tsv,.tab");
});

it("shows the dialog on the upload success event", async () => {
  const DIALOG_TITLE = "Upload success";
  const ROLE_DIALOG = "dialog";

  const { getByRole, queryByRole } = render(UploadingPage);

  expect(queryByRole(ROLE_DIALOG, { name: DIALOG_TITLE }))
    .toBeNull();

  await fireEvent.submit(getByRole("form"));

  expect(getByRole(ROLE_DIALOG))
    .toBeDefined();
  expect(getByRole("heading", { name: DIALOG_TITLE }))
    .toBeDefined();
  expect(getByRole("link", { name: "go to the dashboard" }))
    .toBeDefined();
});

