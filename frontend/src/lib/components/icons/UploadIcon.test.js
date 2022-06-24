import { render } from "@testing-library/svelte";
import UploadIcon from "./UploadIcon.svelte";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(UploadIcon);

  const icon = container.querySelector("svg");
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});
