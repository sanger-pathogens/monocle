import { render } from "@testing-library/svelte";
import InsilicoUploadIcon from "./InsilicoUploadIcon.svelte";

it("renders the composite and hides it for screen readers", () => {
  const { container } = render(InsilicoUploadIcon);

  const icon = container.querySelector("svg");
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});
