import { fireEvent, render } from "@testing-library/svelte";
import Dialog from "./Dialog.svelte";

const CLOSE_BTN_LABEL = "Close dialog";
const DIALOG_SELECTOR = "[role=dialog]";

it("isn't shown when the open prop is false", () => {
  const { container } = render(Dialog, { isOpen: false });

  expect(container.querySelector(DIALOG_SELECTOR)).toBeNull();
});

it("is closed when the close button is clicked", async () => {
  const { container, getByLabelText } =
    render(Dialog, { isOpen: true });

  expect(container.querySelector(DIALOG_SELECTOR))
    .not.toBeNull();

  await fireEvent.click(getByLabelText(CLOSE_BTN_LABEL));

  expect(container.querySelector(DIALOG_SELECTOR))
    .toBeNull();
});

it("is closed when the background is clicked", async () => {
  const { container } = render(Dialog, { isOpen: true });

  expect(container.querySelector(DIALOG_SELECTOR))
    .not.toBeNull();

  const background = container.querySelector(DIALOG_SELECTOR);
  await fireEvent.click(background);

  expect(container.querySelector(DIALOG_SELECTOR))
    .toBeNull();
});

it("isn't closed when the content is clicked", async () => {
  const { container } = render(Dialog, { isOpen: true });

  await fireEvent.click(container.querySelector(".content"));

  expect(container.querySelector(DIALOG_SELECTOR)).not.toBeNull();
});

