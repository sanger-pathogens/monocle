import { render } from "@testing-library/svelte";
import FilterMenuIcon from "./FilterMenuIcon.svelte";

it("renders the icon", () => {
  const { container } = render(FilterMenuIcon);

  expect(container.querySelector("path")).toBeDefined();
});
