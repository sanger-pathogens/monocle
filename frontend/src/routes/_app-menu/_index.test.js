import { render } from "@testing-library/svelte";
import { writable } from "svelte/store";
import AppMenu from "./_index.svelte";

const USER_ROLE_ADMIN = "admin";

it("displays all links by default", () => {
  const { getByLabelText } = render(AppMenu, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  expect(getByLabelText("View and download sample data")).toBeDefined();
  expect(getByLabelText("Upload metadata")).toBeDefined();
  expect(getByLabelText("Upload QC data")).toBeDefined();
  expect(getByLabelText("Upload in-silico data")).toBeDefined();
});

it("can hide the links", () => {
  const { queryByRole } = render(AppMenu, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
    sampleDataLink: false,
    metadataUploadLink: false,
    qcDataUploadLink: false,
    inSilicoDataUploadLink: false,
  });

  expect(queryByRole("link")).toBeNull();
});

it("displays the upload links menu at the expected hight when the data viewer link isn't shown", async () => {
  const uploadLinksMenuSelector = "nav nav";
  const { component, container } = render(AppMenu, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  expect(container.querySelector(uploadLinksMenuSelector).style.top).toBe(
    "4rem"
  );

  await component.$set({ sampleDataLink: false });

  expect(container.querySelector(uploadLinksMenuSelector).style.top).toBe(
    "2rem"
  );
});
