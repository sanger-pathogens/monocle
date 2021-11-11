import { render } from "@testing-library/svelte";
import LoadingIndicator from "./LoadingIndicator.svelte";

it("can display a message", () => {
  const message = "Please wait while machine elves doing their magic.";

  const { getByLabelText, getByText } = render(LoadingIndicator, { message });

  expect(getByText(message).getAttribute("aria-hidden"))
    .toBe("true");
  expect(getByLabelText(message)).toBeDefined();
});

it("can be displayed mid screen", () => {
  const { getByLabelText } = render(LoadingIndicator, { midscreen: true });

  expect(getByLabelText("please wait").getAttribute("style"))
    .toBe("position: absolute; transform: translateX(-50%); left: 50vw; top: 37vh");
});
