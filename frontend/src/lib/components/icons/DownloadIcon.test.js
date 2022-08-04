import { render } from "@testing-library/svelte";
import DownloadIcon from "./DownloadIcon.svelte";

it("renders the icon", () => {
  const { container } = render(DownloadIcon);

  expect(container.querySelector("path")).toBeDefined();
});
