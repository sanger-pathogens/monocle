import { render } from "@testing-library/svelte";
import LoadingIndicator from "./LoadingIndicator.svelte";

const LABEL_LOADING_TEXT = "please wait";

it("can display a message", () => {
  const message = "Please wait while machine elves doing their magic.";

  const { getByLabelText, getByText } = render(LoadingIndicator, { message });

  expect(getByText(message).getAttribute("aria-hidden")).toBe("true");
  expect(getByLabelText(message)).toBeDefined();
});

it("can be displayed mid screen", () => {
  const { getByLabelText } = render(LoadingIndicator, { midscreen: true });

  expect(getByLabelText(LABEL_LOADING_TEXT).getAttribute("style")).toBe(
    "position: absolute; transform: translateX(-50%); left: 50vw; top: 37vh"
  );
});

it("can be displayed w/ a simplified indicator instead", () => {
  const { container, getByLabelText } = render(LoadingIndicator, {
    simple: true,
  });

  expect(getByLabelText(LABEL_LOADING_TEXT)).toBeDefined();
  expect(container.querySelector(".cssload-wrap")).toBeNull();
});

it("can display the simplified indicator w/ a message", () => {
  const loadingMessage = "this may take a while";
  const { container, queryByLabelText, getByLabelText } = render(
    LoadingIndicator,
    { simple: true, message: loadingMessage }
  );

  expect(getByLabelText(loadingMessage)).toBeDefined();
  expect(queryByLabelText(LABEL_LOADING_TEXT)).toBeNull();
  expect(container.querySelector(".cssload-wrap")).toBeNull();
});
