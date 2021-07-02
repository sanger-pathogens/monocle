import { render } from "@testing-library/svelte";
import DashboardPage from "./index.svelte";

it("displays the project progress chart", async () => {
  const { component, getByText } = render(DashboardPage);

  expect(getByText("Project Progress")).toBeDefined();
});

