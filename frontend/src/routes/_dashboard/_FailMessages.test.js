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

it("displays the dialog w/ failures only when the button is clicked", async () => {
  const roleDialog = "dialog";
  const roleTableCell = "cell";
  const failures = [1, 2, 3].map((id) => (
    { lane: `ln${id}`, stage: `stage ${id}`, issue: `Error message ${id}` }
  ));
  const { getByRole, queryByRole } = render(FailMessages, {
    failures,
    title: FAIL_MESSAGES_TITLE
  });

  expect(queryByRole(roleDialog)).toBeNull();

  await fireEvent.click(queryByRole("button"));

  expect(getByRole(roleDialog))
    .toBeDefined();
  expect(getByRole("heading", { name: FAIL_MESSAGES_TITLE }))
    .toBeDefined();
  failures.forEach(({ lane, stage, issue }) => {
    expect(getByRole(roleTableCell, { name: lane }))
      .toBeDefined();
    expect(getByRole(roleTableCell, { name: stage }))
      .toBeDefined();
    expect(getByRole(roleTableCell, { name: issue }))
      .toBeDefined();
  });
});

