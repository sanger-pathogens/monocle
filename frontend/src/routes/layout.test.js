import { render, waitFor } from "@testing-library/svelte";
import { HTTP_HEADER_CONTENT_TYPE, HTTP_HEADERS_JSON } from "$lib/constants.js";
import Layout from "./+layout.svelte";

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    headers: { get: () => HTTP_HEADERS_JSON[HTTP_HEADER_CONTENT_TYPE] },
    json: () => Promise.resolve(),
  })
);

it("loads a script w/ simple-cookie library", () => {
  document.head.appendChild = jest.fn();

  render(Layout);

  const actualScriptElement = document.head.appendChild.mock.calls[4][0];
  expect(actualScriptElement.src).toBe(
    `${global.location.origin}/files/simplecookie.min.js`
  );
  expect(actualScriptElement.async).toBeTruthy();
});

it("fetches a user role", async () => {
  fetch.mockClear();

  render(Layout);

  // Called two times because there's another fetch call for project information.
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch).toHaveBeenCalledWith("/dashboard-api/get_user_details");
});

it("doesn't crash and logs an error when saving a user role fails", async () => {
  const errorMessage = "some error";
  fetch.mockRejectedValueOnce(errorMessage);
  global.console.error = jest.fn();

  const { getByRole } = render(Layout);

  await waitFor(() => {
    expect(
      getByRole("heading", { name: "Monocle Status Monitor" })
    ).toBeDefined();
    expect(console.error).toHaveBeenCalledWith(errorMessage);
  });
});

it("fetches project information", async () => {
  global.fetch.mockClear();

  render(Layout);

  // Called two times because there's another fetch call for a user role.
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch).toHaveBeenCalledWith("/dashboard-api/project");
});
