import { render } from "@testing-library/svelte";
import BulkDownloadIcon from "./BulkDownloadIcon.svelte";

it("renders the icon", () => {
  const { container } = render(BulkDownloadIcon);

  expect(container.querySelector("path")).toBeDefined();
});
