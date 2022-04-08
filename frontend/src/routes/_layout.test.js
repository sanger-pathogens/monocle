import { render, waitFor } from "@testing-library/svelte";
import { getStores } from "$app/stores";
import Layout from "./__layout.svelte";

const USER_ROLE = "support";

getStores.mockReturnValue({ session: { set: jest.fn() } });

global.fetch = jest.fn(() => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({
    user_details: { type: USER_ROLE }
  })
}));

jest.mock("$app/stores", () => ({
  getStores: jest.fn()
}));

it("loads a script w/ simple-cookie library", () => {
  document.head.appendChild = jest.fn();

  render(Layout);

  const actualScriptElement = document.head.appendChild.mock.calls[3][0];
  expect(actualScriptElement.src).toBe(`${global.location.origin}/files/simplecookie.min.js`);
  expect(actualScriptElement.async).toBeTruthy();
});

it("stores a fetched user role in the session", async () => {
  fetch.mockClear();

  render(Layout);

  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith("/dashboard-api/get_user_details");
  const sessionStore = getStores().session;
  await waitFor(() => {
    expect(sessionStore.set).toHaveBeenCalledTimes(1);
    expect(sessionStore.set).toHaveBeenCalledWith({ user: { role: USER_ROLE } });
  });
});

it("doesn't crash and logs an error when saving a user role fails", async () => {
  const errorMessage = "some error";
  fetch.mockRejectedValueOnce(errorMessage);
  global.console.error = jest.fn();

  const { getByRole } = render(Layout);

  await waitFor(() => {
    expect(getByRole("heading", { name: "Monocle" }))
      .toBeDefined();
    expect(console.error).toHaveBeenCalledWith(errorMessage);
  });
});
