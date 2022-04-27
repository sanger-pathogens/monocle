import { render, waitFor } from "@testing-library/svelte";
import { beforeNavigate, goto } from "$app/navigation";
import { getStores } from "$app/stores";
import { PATHNAME_LOGIN } from "$lib/constants.js";
import Layout from "./__layout.svelte";

const AUTH_COOKIE = "nginxauth=fake-auth-token";
const USER_ROLE = "support";

global.fetch = jest.fn(() => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({
    user_details: { type: USER_ROLE }
  })
}));

jest.mock("$app/navigation", () => ({
  beforeNavigate: jest.fn(),
  goto: jest.fn()
}));

jest.mock("$app/stores", () => ({
  getStores: jest.fn()
}));

getStores.mockReturnValue({ session: { set: jest.fn() } });

beforeEach(() => {
  beforeNavigate.mockClear();
  goto.mockClear();
  document.cookie = AUTH_COOKIE;
});

it("stores a fetched user role in the session", async () => {
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

it("redirects to the login page if unauthenticated on the initial render", () => {
  removeAuthCookie();

  render(Layout);

  expect(goto).toHaveBeenCalledTimes(1);
  expect(goto).toHaveBeenCalledWith(PATHNAME_LOGIN);
});

it("doesn't redirect to the login page if authenticated on the initial render", async () => {
  await render(Layout);

  expect(goto).not.toHaveBeenCalled();
});

describe("before navigate", () => {
  it("redirects to the login page if unauthenticated", async () => {
    removeAuthCookie();
    render(Layout);
    const beforeNavigateCallback = beforeNavigate.mock.calls[0][0];
    const cancel = jest.fn();
    goto.mockClear();

    await beforeNavigateCallback({ cancel });

    expect(beforeNavigate).toHaveBeenCalledTimes(1);
    expect(cancel).toHaveBeenCalledTimes(1);
    expect(goto).toHaveBeenCalledTimes(1);
    expect(goto).toHaveBeenCalledWith(PATHNAME_LOGIN);
  });

  it("doesn't redirect to the login page if unauthenticated and already navigating to the login page", async () => {
    removeAuthCookie();
    render(Layout);
    const beforeNavigateCallback = beforeNavigate.mock.calls[0][0];
    const cancel = jest.fn();
    goto.mockClear();

    await beforeNavigateCallback({ cancel, to: { pathname: PATHNAME_LOGIN } });

    expect(beforeNavigate).toHaveBeenCalledTimes(1);
    expect(cancel).not.toHaveBeenCalled();
    expect(goto).not.toHaveBeenCalledTimes(1);
  });

  it("redirects to the root page if authenticated and navigating to the login page", async () => {
    render(Layout);
    const beforeNavigateCallback = beforeNavigate.mock.calls[0][0];
    const cancel = jest.fn();
    goto.mockClear();

    await beforeNavigateCallback({ cancel, to: { pathname: PATHNAME_LOGIN } });

    expect(beforeNavigate).toHaveBeenCalledTimes(1);
    expect(cancel).toHaveBeenCalledTimes(1);
    expect(goto).toHaveBeenCalledTimes(1);
    expect(goto).toHaveBeenCalledWith("/");
  });

  it("doesn't redirect to the root page if authenticated and navigating elsewhere", async () => {
    render(Layout);
    const beforeNavigateCallback = beforeNavigate.mock.calls[0][0];
    const cancel = jest.fn();
    goto.mockClear();

    await beforeNavigateCallback({ cancel, to: { pathname: "/some-path" } });

    expect(beforeNavigate).toHaveBeenCalledTimes(1);
    expect(cancel).not.toHaveBeenCalled();
    expect(goto).not.toHaveBeenCalledTimes(1);
  });
});

function removeAuthCookie() {
  document.cookie = "nginxauth=1; expires=1 Jan 1970 00:00:00 GMT;";
}
