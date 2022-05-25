import { render } from "@testing-library/svelte";
import SettingsIcon from "./SettingsIcon.svelte";

it("is rendered and is hidden for screen readers", () => {
  const { container } = render(SettingsIcon);

  const icon = container.querySelector("svg");
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

it("can be rendered w/ a custom color", () => {
  const color = "blue";
  const { container } = render(SettingsIcon, { color });

  expect(container.querySelector("svg").getAttribute("fill")).toBe(color);
});
