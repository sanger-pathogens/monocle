import { render } from "@testing-library/svelte";
import Header from "$lib/components/layout/Header.svelte";

const LABEL_LOG_OUT = "Log out";
const ROLE_LINK = "link";

it("shows a logout link", () => {
  const { getByRole } = render(Header);
  const linkElement = getByRole(ROLE_LINK, { name: LABEL_LOG_OUT });

  expect(linkElement.href).toBe("http://localhost/logout");
  expect(linkElement.rel).toBe("external");
});

it("doesn't show a logout link on the login page", () => {
  delete global.location;
  global.location = new URL("http://localhost/login");
  const { queryByRole } = render(Header);

  expect(queryByRole(ROLE_LINK, { name: LABEL_LOG_OUT }))
    .toBeNull();
});
