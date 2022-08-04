import { render } from "@testing-library/svelte";
import FilterIcon from "./FilterIcon.svelte";

it("renders the icon", () => {
  const { container } = render(FilterIcon);

  expect(container.querySelector("path")).toBeDefined();
});
