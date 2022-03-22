import { render } from "@testing-library/svelte";
import InsilicoUploadIcon from "./InsilicoUploadIcon.svelte";

it("renders the composite and hides it for screen readers", () => {
  const { container } = render(InsilicoUploadIcon);

  const icons = Array.from(container.querySelectorAll("svg"));
  expect(icons).toHaveLength(2);
  icons.forEach((icon) => {
    expect(icon.getAttribute("aria-hidden")).toBe("true");
  });
});

