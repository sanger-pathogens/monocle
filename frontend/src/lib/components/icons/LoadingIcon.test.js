import { render } from "@testing-library/svelte";
import LoadingIcon from "./LoadingIcon.svelte";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(LoadingIcon);

  const icon = container.querySelector("svg");
  expect(icon).toBeDefined();
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});
