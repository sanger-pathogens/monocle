import { render } from "@testing-library/svelte";
import SampleDataViewerIcon from "./SampleDataViewerIcon.svelte";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(SampleDataViewerIcon);

  const icon = container.querySelector("svg");
  expect(icon).toBeDefined();
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

