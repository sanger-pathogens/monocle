import { render } from "@testing-library/svelte";
import { writable } from "svelte/store";
import Header from "$lib/components/layout/Header.svelte";

jest.mock("$app/stores", () => ({
  getStores: jest.fn(() => ({
    session: {
      subscribe: () => ({ unsubscribe: () => ({}) }),
    },
  })),
}));

const LABEL_LOG_OUT = "Log out";
const ROLE_LINK = "link";

it("shows a logout link", () => {
  const { getByRole } = render(Header, { session: writable({}) });
  const linkElement = getByRole(ROLE_LINK, { name: LABEL_LOG_OUT });

  expect(linkElement.href).toBe("http://localhost/logout");
  expect(linkElement.rel).toBe("external");
});

it("doesn't show a logout link on the login page", () => {
  delete global.location;
  global.location = new URL("http://localhost/login");
  const { queryByRole } = render(Header, { session: writable({}) });

  expect(queryByRole(ROLE_LINK, { name: LABEL_LOG_OUT })).toBeNull();
});
