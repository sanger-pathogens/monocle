import { render } from "@testing-library/svelte";
import { session } from '$app/stores';
import DashboardPage from "./index.svelte";

// Mocking this module for the whole file is a workaround
// for Jest's not parsing SvelteKit's $app modules.
jest.mock("$app/stores", async () => {
  const { writable } = await import("svelte/store");
  return { session: writable() };
});

it("displays the project progress chart", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("Project Progress")).toBeDefined();
});

it("displays the upload link", () => {
  const { findByRole } = render(DashboardPage, { institutions: [] });

  expect(findByRole("link", { name: "Upload metadata" }))
    .toBeDefined();
});

it("displays status for each institution passed", () => {
  const institutions = [{
    name: "Center for Reducing Suffering",
    key: "CRS",
    batches: { received: 1, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  }, {
    name: "Qualia Research Institute",
    key: "QRI",
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  }];

  const { component, getByText } = render(DashboardPage, { institutions });

  institutions.forEach(({ name }) => {
    const institutionHeadingElement = getByText(name);
    const institutionStatusPanes = institutionHeadingElement.parentElement
      .querySelectorAll(":scope > article");
    expect(institutionStatusPanes).toHaveLength(3);
  });
});

it("displays a message when no institutions passed", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("No institutions found for this account", { exact: false }))
    .toBeDefined();
});

