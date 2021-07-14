import { render } from "@testing-library/svelte";
import DashboardPage from "./index.svelte";

it("displays the project progress chart", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("Project Progress")).toBeDefined();
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

