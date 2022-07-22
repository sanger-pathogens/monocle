import { fireEvent, render } from "@testing-library/svelte";
import UploadingPage from "./index.svelte";
import { writable } from "svelte/store";

const UPLOAD_URL = "/metadata/juno/metadata-upload";
const PROJECT = {
  project: { upload_links: [{ label: "metadata", url: UPLOAD_URL }] },
};
const ROLE_FORM = "form";

it("is rendered w/ the data upload form", () => {
  const { container, getByRole } = render(UploadingPage, {
    session: writable(PROJECT),
  });
  expect(container.querySelector("p").textContent).toBe(
    "Select or drag and drop your CSV files (saved as UTF-8) with sample metadata:"
  );
  expect(getByRole(ROLE_FORM)).toBeDefined();
});

it("has the expected upload URL", async () => {
  global.fetch = jest.fn(() => Promise.resolve());
  const { container, getByRole } = render(UploadingPage, {
    session: writable(PROJECT),
  });
  fireEvent.change(container.querySelector("input[type=file]"), {
    target: { files: ["some.file"] },
  });

  await fireEvent.submit(getByRole(ROLE_FORM));

  const actualUploadUrl = fetch.mock.calls[0][0];
  expect(actualUploadUrl).toBe(UPLOAD_URL);
});

it("shows the dialog on the upload success event", async () => {
  const DIALOG_TITLE = "Upload success";
  const ROLE_DIALOG = "dialog";
  const ROLE_HEADING = "heading";

  const { getByRole, queryByRole } = render(UploadingPage, {
    session: writable(PROJECT),
  });

  expect(queryByRole(ROLE_DIALOG)).toBeNull();
  expect(queryByRole(ROLE_HEADING, { name: DIALOG_TITLE })).toBeDefined();

  await fireEvent.submit(getByRole(ROLE_FORM));

  expect(getByRole(ROLE_DIALOG)).toBeDefined();
  expect(getByRole(ROLE_HEADING, { name: DIALOG_TITLE })).toBeDefined();
  expect(getByRole("link", { name: "go to the dashboard" })).toBeDefined();
});
