import { render } from "@testing-library/svelte";
import LoadingIcon from "./LoadingIcon.svelte";

it("renders the icon w/ the expected CSS class for animation", () => {
  const { container } = render(LoadingIcon);

  expect(container.querySelector(".spinner path")).toBeDefined();
});
