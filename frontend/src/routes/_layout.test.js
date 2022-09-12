import { render, waitFor } from "@testing-library/svelte";
import { get, writable } from "svelte/store";
import { HTTP_HEADER_CONTENT_TYPE, HTTP_HEADERS_JSON } from "$lib/constants.js";
import Layout from "./__layout.svelte";

const USER_ROLE = "support";

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    headers: { get: () => HTTP_HEADERS_JSON[HTTP_HEADER_CONTENT_TYPE] },
    json: () =>
      Promise.resolve({
        user_details: { type: USER_ROLE },
      }),
  })
);

it("loads a script w/ simple-cookie library", () => {
  document.head.appendChild = jest.fn();

  render(Layout, { session: writable({}) });

  const actualScriptElement = document.head.appendChild.mock.calls[4][0];
  expect(actualScriptElement.src).toBe(
    `${global.location.origin}/files/simplecookie.min.js`
  );
  expect(actualScriptElement.async).toBeTruthy();
});

it("stores a fetched user role in the session", async () => {
  const sessionStore = writable({});
  jest.spyOn(sessionStore, "update");
  fetch.mockClear();

  render(Layout, { session: sessionStore });

  // Called two times because there's another fetch call for project information.
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch).toHaveBeenCalledWith("/dashboard-api/get_user_details");
  await waitFor(() => {
    // The session is updated two times because we also set project information once it's
    // fetched elsewhere.
    expect(sessionStore.update).toHaveBeenCalledTimes(2);

    expect(get(sessionStore).user).toStrictEqual({ role: USER_ROLE });
  });
});

it("doesn't crash and logs an error when saving a user role fails", async () => {
  const errorMessage = "some error";
  fetch.mockRejectedValueOnce(errorMessage);
  global.console.error = jest.fn();

  const { getByRole } = render(Layout, { session: writable({}) });

  await waitFor(() => {
    expect(getByRole("heading", { name: "Monocle" })).toBeDefined();
    expect(console.error).toHaveBeenCalledWith(errorMessage);
  });
});

it("stores fetched project information in the session", async () => {
  const project = "some project data";
  const sessionStore = writable({});
  jest.spyOn(sessionStore, "update");
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      headers: { get: () => HTTP_HEADERS_JSON[HTTP_HEADER_CONTENT_TYPE] },
      json: () => Promise.resolve({ project }),
    })
  );

  render(Layout, { session: sessionStore });

  // Called two times because there's another fetch call for a user role.
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch).toHaveBeenCalledWith("/dashboard-api/project");
  await waitFor(() => {
    expect(sessionStore.update).toHaveBeenCalledTimes(1);

    expect(get(sessionStore).project).toBe(project);
  });
});
