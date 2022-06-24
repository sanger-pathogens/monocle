import { render } from "@testing-library/svelte";
import RemoveFilterIcon from "./RemoveFilterIcon.svelte";

it("is rendered and is hidden for screen readers", () => {
  const { container } = render(RemoveFilterIcon);

  const icon = container.querySelector("svg");
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

it("can be rendered w/ a custom color", () => {
  const color = "blue";
  const { container } = render(RemoveFilterIcon, { color });

  expect(container.querySelector("path").getAttribute("fill")).toBe(color);
});
