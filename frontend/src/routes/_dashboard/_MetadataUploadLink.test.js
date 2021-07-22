import { render } from "@testing-library/svelte";
import { session } from "$app/stores";
import MetadataUploadLink from "./_MetadataUploadLink.svelte";

const LINK_TITLE = "Upload metadata";
const SEMANTIC_ROLE_LINK = "link";
const USER_ROLE_ADMIN = "admin";

// Mocking this module for the whole file is a workaround
// for Jest's not parsing SvelteKit's $app modules.
jest.mock("$app/stores", async () => {
  const { writable } = await import("svelte/store");
  return { session: writable({ user: { role: USER_ROLE_ADMIN } }) };
});

//FIXME: mock `session` and unskip the tests (Nil's spent hours on this in vain).
it.skip("is hidden if the user isn't admin", () => {
  const { queryByRole } = render(MetadataUploadLink);

  expect(queryByRole(SEMANTIC_ROLE_LINK, { name: LINK_TITLE }))
    .toBeDefined();

  session.set({ user: { role: "collaborator" } });

  expect(queryByRole(SEMANTIC_ROLE_LINK, { name: LINK_TITLE }))
    .toBeNull();
});

it.skip("has the correct URL", () => {
  const { queryByRole } = render(MetadataUploadLink);

  const actualUploadURL = queryByRole(SEMANTIC_ROLE_LINK, { name: LINK_TITLE })
    .getAttribute("href");
  expect(actualUploadURL).toBe("/upload");
});

