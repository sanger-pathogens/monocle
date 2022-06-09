import { fireEvent, render } from "@testing-library/svelte";
import Dialog from "./Dialog.svelte";

const LABEL_CLOSE_BTN = "Close dialog";
const LABEL_DIALOG = "dialog title";

it("isn't shown when the open prop is false", () => {
  const { queryByLabelText } = render(Dialog, {
    isOpen: false,
    ariaLabel: LABEL_DIALOG,
  });

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

it("is hidden w/ CSS only when `persistState` prop is passed", () => {
  const { getByLabelText } = render(Dialog, {
    isOpen: false,
    persistState: true,
    ariaLabel: LABEL_DIALOG,
  });

  expect(getByLabelText(LABEL_DIALOG).style.display).toBe("none");
});

it("is closed when the close button is clicked", async () => {
  const { getByLabelText, queryByLabelText } = render(Dialog, {
    isOpen: true,
    ariaLabel: LABEL_DIALOG,
  });

  expect(getByLabelText(LABEL_DIALOG)).toBeDefined();

  await fireEvent.click(getByLabelText(LABEL_CLOSE_BTN));

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

it("is closed when the background is clicked", async () => {
  const { getByLabelText, queryByLabelText } = render(Dialog, {
    isOpen: true,
    ariaLabel: LABEL_DIALOG,
  });

  expect(getByLabelText(LABEL_DIALOG)).toBeDefined();

  const background = getByLabelText(LABEL_DIALOG);
  await fireEvent.click(background);

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

it("isn't closed when the content is clicked", async () => {
  const { container, getByLabelText } = render(Dialog, {
    isOpen: true,
    ariaLabel: LABEL_DIALOG,
  });

  await fireEvent.click(container.querySelector(".content"));

  expect(getByLabelText(LABEL_DIALOG)).toBeDefined();
});
