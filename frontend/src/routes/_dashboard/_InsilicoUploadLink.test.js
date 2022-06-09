import { render, waitFor } from "@testing-library/svelte";
import { writable } from "svelte/store";
import { USER_ROLE_ADMIN } from "$lib/constants.js";
import InsilicoUploadLink from "./_InsilicoUploadLink.svelte";

const LINK_TITLE = "Upload in-silico data";
const ROLE_LINK = "link";

it("is hidden if the user isn't admin", async () => {
  const { component, getByRole, queryByRole } = render(InsilicoUploadLink, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  expect(getByRole(ROLE_LINK, { name: LINK_TITLE })).toBeDefined();

  component.$set({ session: writable({ user: { role: "collaborator" } }) });

  await waitFor(() => {
    expect(queryByRole(ROLE_LINK, { name: LINK_TITLE })).toBeNull();
  });
});

it("has the correct URL", () => {
  const { getByRole } = render(InsilicoUploadLink, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  const actualUploadURL = getByRole(ROLE_LINK, {
    name: LINK_TITLE,
  }).getAttribute("href");
  expect(actualUploadURL).toBe("/in-silico-upload");
});
