import { render } from "@testing-library/svelte";
import DashboardPage from "./index.svelte";

it("displays the project progress chart", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("Project Progress")).toBeDefined();
});

it("displays status for each institution passed", () => {
  const institutions = [{
    name: "Center for Reducing Suffering",
    batches: { received: 0, deliveries: [] }
  }, {
    name: "Qualia Research Institute",
    batches: { received: 42, deliveries: [] }
  }];

  const { component, getByText } = render(DashboardPage, { institutions });

  institutions.forEach(({ name }) => {
    expect(getByText(name)).toBeDefined();
  });
});

it("displays a message when no institutions passed", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("No institutions found for this account", { exact: false }))
    .toBeDefined();
});

