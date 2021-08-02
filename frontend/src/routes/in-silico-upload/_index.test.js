import { render } from "@testing-library/svelte";
import UploadingPage from "./index.svelte";

it("is rendered", () => {
  const { container, getByRole } = render(UploadingPage);

  expect(container.querySelector("p").textContent)
    .toBe("Select or drag and drop your files with in-silico data:");
  expect(getByRole("button", { name: "Upload" }))
    .toBeDefined();
});

