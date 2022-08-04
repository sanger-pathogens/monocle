import { render } from "@testing-library/svelte";
import SettingsIcon from "./SettingsIcon.svelte";

it("renders the icon", () => {
  const { container } = render(SettingsIcon);

  expect(container.querySelector("path")).toBeDefined();
});
