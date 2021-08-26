import { render, waitFor } from "@testing-library/svelte";
import { getStores } from "$app/stores";
import { MONOCLE_URL } from "../dataLoading.js";
import Layout from "./__layout.svelte";

const USER_ROLE = "support";

global.fetch = jest.fn(() => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({
    user_details: { type: USER_ROLE }
  })
}));

jest.mock("$app/stores", () => ({
  getStores: jest.fn()
}));

it("stores a fetched user role in the session", async () => {
  getStores.mockReturnValue({ session: { set: jest.fn() } });

  render(Layout);

  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith(`${MONOCLE_URL}/dashboard-api/get_user_details`);
  const sessionStore = getStores().session;
  await waitFor(() => {
    expect(sessionStore.set).toHaveBeenCalledTimes(1);
    expect(sessionStore.set).toHaveBeenCalledWith({ user: { role: USER_ROLE } });
  });
});
