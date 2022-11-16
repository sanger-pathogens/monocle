import { render } from "@testing-library/svelte";
import { writable } from "svelte/store";
import Header from "$lib/components/layout/Header.svelte";

const BASE_URL = location.origin;
const LABEL_LOG_OUT = "Log out";
const LABEL_PROJECT_NAME = "GPS";
const ROLE_LINK = "link";

it("doesn't display a project logo if the session has no project", () => {
  const { queryByAltText } = render(Header, { session: writable({}) });

  expect(queryByAltText(LABEL_PROJECT_NAME)).toBeNull();
});

it("doesn't display a project logo if the project in the session has no logo URL", () => {
  const { queryByAltText } = render(Header, {
    session: writable({ project: {} }),
  });

  expect(queryByAltText(LABEL_PROJECT_NAME)).toBeNull();
});

it("displays project information from the session", () => {
  const project = {
    name: LABEL_PROJECT_NAME,
    project_url: "project/url",
    logo_url: `${BASE_URL}/img/url.svg`,
    header_links: [
      { url: `${BASE_URL}/some/url`, label: "About" },
      { url: `${BASE_URL}/a/url`, label: "Team" },
    ],
  };
  const { container, getByText, getByAltText } = render(Header, {
    session: writable({ project }),
  });

  const logoImg = getByAltText(project.name);
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
