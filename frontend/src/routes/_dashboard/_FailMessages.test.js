import { fireEvent, render } from "@testing-library/svelte";
import FailMessages from "./_FailMessages.svelte";

const FAIL_MESSAGES_TITLE = "Sequencing Failures";

it("isn't displayed if there are no failures", () => {
  const { container } = render(FailMessages, {
    failures: [],
    title: FAIL_MESSAGES_TITLE
  });

  expect(container.innerHTML).toBe("<div></div>");
});

it("displays the dialog w/ failures only when the button is clicked", () => {
  const roleDialog = "dialog";
  const roleTableCell = "cell";
  const failures = [1, 2, 3].map((id) => (
    { lane: `ln${id}`, stage: `stage ${id}`, issue: `Error message ${id}` }
  ));
  const { queryByRole } = render(FailMessages, {
    failures,
    title: FAIL_MESSAGES_TITLE
  });

  expect(queryByRole(roleDialog)).toBeNull();

  fireEvent.click(queryByRole("button"));

  expect(queryByRole(roleDialog, { name: FAIL_MESSAGES_TITLE }))
    .toBeDefined();
  failures.forEach(({ lane, stage, issue }) => {
    expect(queryByRole(roleTableCell, { name: lane }))
      .toBeDefined();
    expect(queryByRole(roleTableCell, { name: stage }))
      .toBeDefined();
    expect(queryByRole(roleTableCell, { name: issue }))
      .toBeDefined();
  });
});

