import { render } from "@testing-library/svelte";
import LoadingIndicator from "./LoadingIndicator.svelte";

it("can be displayed mid screen", () => {
  const { getByLabelText } = render(LoadingIndicator, { midscreen: true });

  expect(getByLabelText("please wait").getAttribute("style"))
    .toBe("position: absolute; transform: translateX(-50%); left: 50vw; top: 37vh");
});
