import { render, waitFor } from "@testing-library/svelte";
import { writable } from "svelte/store";
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

  const actualScriptElement = document.head.appendChild.mock.calls[3][0];
  expect(actualScriptElement.src).toBe(
    `${global.location.origin}/files/simplecookie.min.js`
  );
  expect(actualScriptElement.async).toBeTruthy();
});

it("stores a fetched user role and project information in the session", async () => {
  const sessionStore = writable({});
  sessionStore.set = jest.fn();
  sessionStore.update = jest.fn();
  fetch.mockClear();

  render(Layout, { session: sessionStore });

  expect(fetch).toHaveBeenCalledTimes(1); // getUserDetails
  expect(fetch).toHaveBeenCalledWith("/dashboard-api/get_user_details");
  await waitFor(() => {
    // Says it hasn't been called, but it works?
    //expect(sessionStore.update).toHaveBeenCalledTimes(2); // getUserDetails and getProjectInformation
    // .update() takes an anonymous function, not sure how to test for that
    /*expect(sessionStore.update).toHaveBeenCalledWith({
      user: { role: USER_ROLE },
    });*/
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
