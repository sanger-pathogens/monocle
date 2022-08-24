import { render } from "@testing-library/svelte";
import { writable } from "svelte/store";
import DataUploadLinks from "./_DataUploadLinks.svelte";

const USER_ROLE_ADMIN = "admin";

it("renders the links w/ the expected labels and URLs", () => {
  const ROLE_LINK = "link";
  const DOMAIN_NAME = window.location.host;

  const { getByRole } = render(DataUploadLinks, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  expect(getByRole(ROLE_LINK, { name: "Upload metadata" }).href).toMatch(
    new RegExp(`${DOMAIN_NAME}/metadata-upload`)
  );
  expect(getByRole(ROLE_LINK, { name: "Upload QC data" }).href).toMatch(
    new RegExp(`${DOMAIN_NAME}/qc-data-upload`)
  );
  expect(getByRole(ROLE_LINK, { name: "Upload in-silico data" }).href).toMatch(
    new RegExp(`${DOMAIN_NAME}/in-silico-upload`)
  );
});

it("shown only to the admin", async () => {
  const sessionStore = writable({});
  const { container, getByLabelText } = render(DataUploadLinks, {
    session: sessionStore,
  });

  expect(container.innerHTML).toBe("<div></div>");

  await sessionStore.set({ user: { role: USER_ROLE_ADMIN } });

  expect(getByLabelText("Upload metadata")).toBeDefined();
});
