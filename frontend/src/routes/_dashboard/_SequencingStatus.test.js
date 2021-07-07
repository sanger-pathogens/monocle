import { render } from "@testing-library/svelte";
import SequencingStatus from "./_SequencingStatus.svelte";

it("displays data passed", () => {
  const received = 30;
  const completed = 10;

  const { container, getByText } = render(SequencingStatus, { sequencingStatus: {
    received,
    completed
  }});

  expect(container.querySelector("h4").textContent)
    .toBe(`${completed} of ${received} Samples Sequenced`);
  expect(getByText("% completed", { exact: false }))
    .toBeDefined();
});

it("displays special title when all samples are sequenced", () => {
  const received = 30;

  const { container } = render(SequencingStatus, { sequencingStatus: {
    received,
    completed: received
  }});

  expect(container.querySelector("h4").textContent)
    .toBe(`All ${received} Samples Sequenced`);
});

