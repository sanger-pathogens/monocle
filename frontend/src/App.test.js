import { fireEvent, render } from "@testing-library/svelte";
import App from "./App.svelte";

it("renders the metadata uploading component", () => {
  const { getByText } = render(App);

  expect(getByText("Select or drag and drop your Excel files with sample metadata:"))
    .toBeDefined();
  expect(getByText("Upload"))
    .toBeDefined();
});

it("redirects to the dashboard page on the upload success event", async () => {
  const redirectionSpy = jest.fn();
  const injectedWindow = {
    location: { assign: redirectionSpy }
  };
  const { container } = render(App, { injectedWindow });

  expect(redirectionSpy).not.toHaveBeenCalled();

  await fireEvent.submit(container.querySelector("form"));

  expect(redirectionSpy).toHaveBeenCalledTimes(1);
  expect(redirectionSpy).toHaveBeenCalledWith("/dashboard");
});

