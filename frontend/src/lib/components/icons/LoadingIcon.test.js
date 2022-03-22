import { render } from "@testing-library/svelte";
import LoadingIcon from "./LoadingIcon.svelte";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(LoadingIcon);

  const icon = container.querySelector("svg");
  expect(icon).toBeDefined();
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

it("doesn't hide the icon from screen readers if `label` is passed", () => {
  const iconLabel = "please wait";
  const { container, getByText } = render(LoadingIcon, { label: iconLabel });

  expect(getByText(iconLabel)).toBeDefined();
  const icon = container.querySelector("svg");
  expect(icon.getAttribute("aria-hidden")).toBeNull();
});
