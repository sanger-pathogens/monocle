import { render } from "@testing-library/svelte";
import DownloadIcon from "./DownloadIcon.svelte";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(DownloadIcon);

  const icon = container.querySelector("svg");
  expect(icon).toBeDefined();
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

