import { fireEvent, render } from "@testing-library/svelte";
import { goto } from '$app/navigation';
import UploadingPage from "./index.svelte";

// Mocking this module for the whole file is a workaround
// for Jest's not understanding SvelteKit's $app modules.
jest.mock('$app/navigation', () => ({
  goto: jest.fn()
}));

it("renders the metadata uploading component", () => {
  const { getByText } = render(UploadingPage);

  expect(getByText("Select or drag and drop your Excel files with sample metadata:"))
    .toBeDefined();
  expect(getByText("Upload"))
    .toBeDefined();
});

it("redirects to the dashboard page on the upload success event", async () => {
  const { container } = render(UploadingPage);

  expect(goto).not.toHaveBeenCalled();

  await fireEvent.submit(container.querySelector("form"));

  expect(goto).toHaveBeenCalledTimes(1);
  expect(goto).toHaveBeenCalledWith("/");
});

