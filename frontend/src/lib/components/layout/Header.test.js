import { render } from "@testing-library/svelte";
import { writable } from "svelte/store";
import Header from "$lib/components/layout/Header.svelte";

const BASE_URL = location.origin;
const LABEL_LOG_OUT = "Log out";
const ROLE_IMAGE = "img";
const ROLE_LINK = "link";

it("doesn't display a logo if the session has no project", () => {
  const { queryByRole } = render(Header, { session: writable({}) });

  expect(queryByRole(ROLE_IMAGE)).toBeNull();
});

it("doesn't display a logo if the project in the session has no logo URL", () => {
  const { queryByRole } = render(Header, {
    session: writable({ project: {} }),
  });

  expect(queryByRole(ROLE_IMAGE)).toBeNull();
});

it("displays project information form the session", () => {
  const project = {
    name: "JUNO",
    project_url: "project/url",
    logo_url: `${BASE_URL}/img/url.svg`,
    header_links: [
      { url: `${BASE_URL}/some/url`, label: "About" },
      { url: `${BASE_URL}/a/url`, label: "Team" },
    ],
  };
  const { container, getByText, getByRole } = render(Header, {
    session: writable({ project }),
  });

  const logoImg = getByRole(ROLE_IMAGE);
  expect(logoImg.alt).toBe(project.name);
  expect(logoImg.src).toBe(project.logo_url);
  expect(
    container.querySelector(`a[href="${project.project_url}"]`)
  ).not.toBeNull();
  project.header_links.forEach(({ url, label }) =>
    expect(getByText(label).href).toBe(url)
  );
});

it("shows a logout link", () => {
  const { getByRole } = render(Header, { session: writable({}) });
  const linkElement = getByRole(ROLE_LINK, { name: LABEL_LOG_OUT });

  expect(linkElement.href).toBe(`${BASE_URL}/logout`);
  expect(linkElement.rel).toBe("external");
});

it("doesn't show a logout link on the login page", () => {
  delete global.location;
  global.location = new URL(`${BASE_URL}/login`);
  const { queryByRole } = render(Header, { session: writable({}) });

  expect(queryByRole(ROLE_LINK, { name: LABEL_LOG_OUT })).toBeNull();
});
