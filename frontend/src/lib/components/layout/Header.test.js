import { render } from "@testing-library/svelte";
import Header from "$lib/components/layout/Header.svelte";

const BASE_URL = location.origin;
const LABEL_LOG_OUT = "Log out";
const LABEL_PROJECT_NAME = "GPS";
const ROLE_LINK = "link";

it("doesn't display a project logo if the project is empty", () => {
  const { queryByAltText } = render(Header, { projectState: undefined });

  expect(queryByAltText(LABEL_PROJECT_NAME)).toBeNull();
});

it("doesn't display a project logo if the project has no logo URL", () => {
  const { queryByAltText } = render(Header, {
    projectState: {},
  });

  expect(queryByAltText(LABEL_PROJECT_NAME)).toBeNull();
});

it("displays project information", () => {
  const projectState = {
    name: LABEL_PROJECT_NAME,
    projectUrl: "project/url",
    logoUrl: `${BASE_URL}/img/url.svg`,
    headerLinks: [
      { url: `${BASE_URL}/some/url`, label: "About" },
      { url: `${BASE_URL}/a/url`, label: "Team" },
    ],
  };
  const { container, getByText, getByAltText } = render(Header, {
    projectState,
  });

  const logoImg = getByAltText(projectState.name);
  expect(logoImg.alt).toBe(projectState.name);
  expect(logoImg.src).toBe(projectState.logoUrl);
  expect(
    container.querySelector(`a[href="${projectState.projectUrl}"]`)
  ).not.toBeNull();
  projectState.headerLinks.forEach(({ url, label }) =>
    expect(getByText(label).href).toBe(url)
  );
});

it("shows a logout link", () => {
  const { getByRole } = render(Header, { projectState: undefined });
  const linkElement = getByRole(ROLE_LINK, { name: LABEL_LOG_OUT });

  expect(linkElement.href).toBe(`${BASE_URL}/logout`);
  expect(linkElement.rel).toBe("external");
});

it("doesn't show a logout link on the login page", () => {
  delete global.location;
  global.location = new URL(`${BASE_URL}/login`);
  const { queryByRole } = render(Header, { projectState: undefined });

  expect(queryByRole(ROLE_LINK, { name: LABEL_LOG_OUT })).toBeNull();
});
