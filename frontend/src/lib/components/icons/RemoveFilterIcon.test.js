import { render } from "@testing-library/svelte";
import RemoveFilterIcon from "./RemoveFilterIcon.svelte";

it("renders the icon", () => {
  const { container } = render(RemoveFilterIcon);

  expect(container.querySelector("path")).toBeDefined();
});
