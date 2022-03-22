import { render } from "@testing-library/svelte";
import InsilicoIcon from "./InsilicoIcon.svelte";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(InsilicoIcon);

  const icon = container.querySelector("svg");
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

