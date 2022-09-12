import { render } from "@testing-library/svelte";
import HelpIcon from "./HelpIcon.svelte";

it("renders the icon", () => {
  const { container } = render(HelpIcon);

  expect(container.querySelector("path")).toBeDefined();
});
