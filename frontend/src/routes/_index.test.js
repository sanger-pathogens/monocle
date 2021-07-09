import { render } from "@testing-library/svelte";
import DashboardPage from "./index.svelte";

it("displays the project progress chart", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("Project Progress")).toBeDefined();
});

//FIXME: unskip once the pipeline status pane is ready
it.skip("displays status for each institution passed", () => {
  const institutions = [{
    name: "Center for Reducing Suffering",
    key: "CRS",
    batches: { received: 0, deliveries: [] },
    sequencingStatus: {}
  }, {
    name: "Qualia Research Institute",
    key: "QRI",
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {}
  }];

  const { component, getByText } = render(DashboardPage, { institutions });

  institutions.forEach(({ name }) => {
    const institutionHeadingElement = getByText(name);
    const institutionStatusPanes = institutionHeadingElement.parentElement
      .querySelectorAll("h3 ~ article");
    expect(institutionStatusPanes).toHaveLength(3);
  });
});

it("displays a message when no institutions passed", () => {
  const { getByText } = render(DashboardPage, { institutions: [] });

  expect(getByText("No institutions found for this account", { exact: false }))
    .toBeDefined();
});

