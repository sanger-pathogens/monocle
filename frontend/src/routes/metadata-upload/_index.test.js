import { fireEvent, render } from "@testing-library/svelte";
import UploadingPage from "./index.svelte";

it("is rendered w/ the data upload form", () => {
  const { container, getByRole } = render(UploadingPage);

  expect(container.querySelector("p").textContent).toBe(
    "Select or drag and drop your CSV files (saved as UTF-8) with sample metadata:"
  );
  expect(getByRole("form")).toBeDefined();
});

it("shows the dialog on the upload success event", async () => {
  const DIALOG_TITLE = "Upload success";
  const ROLE_DIALOG = "dialog";
  const ROLE_HEADING = "heading";

  const { getByRole, queryByRole } = render(UploadingPage);

  expect(queryByRole(ROLE_DIALOG)).toBeNull();
  expect(queryByRole(ROLE_HEADING, { name: DIALOG_TITLE })).toBeDefined();

  await fireEvent.submit(getByRole("form"));

  expect(getByRole(ROLE_DIALOG)).toBeDefined();
  expect(getByRole(ROLE_HEADING, { name: DIALOG_TITLE })).toBeDefined();
  expect(getByRole("link", { name: "go to the dashboard" })).toBeDefined();
});
