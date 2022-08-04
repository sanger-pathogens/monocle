import { render } from "@testing-library/svelte";
import SampleDataViewerIcon from "./SampleDataViewerIcon.svelte";

it("renders the icon", () => {
  const { container } = render(SampleDataViewerIcon);

  expect(container.querySelector("path")).toBeDefined();
});
