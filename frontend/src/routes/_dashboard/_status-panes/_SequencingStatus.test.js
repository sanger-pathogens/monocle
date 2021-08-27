import { fireEvent, render } from "@testing-library/svelte";
import SequencingStatus from "./_SequencingStatus.svelte";

const FAILED = 2;
const RECEIVED = 10;

it("displays data passed", () => {
  const completed = 8;

  const { container, getByText } = render(SequencingStatus, {
    sequencingStatus: {
      received: RECEIVED,
      completed
    },
  });

  expect(container.querySelector("h4").textContent)
    .toBe(`${completed} of ${RECEIVED} Samples Sequenced`);
  expect(getByText("% completed", { exact: false }))
    .toBeDefined();
});

it("displays a special heading when all samples are sequenced", () => {
  const { container } = render(SequencingStatus, {
    sequencingStatus: {
      received: RECEIVED,
      completed: RECEIVED
    },
  });

  expect(container.querySelector("h4").textContent)
    .toBe(`All ${RECEIVED} Samples Sequenced`);
});

it("displays the download button", () => {
  const succeeded = RECEIVED - FAILED;

  const { getByRole } = render(SequencingStatus, {
    sequencingStatus: {
      received: RECEIVED,
      completed: RECEIVED,
      success: succeeded,
    },
  });

  expect(getByRole("button", { name: `Download ${succeeded} successfully sequenced samples` }))
    .toBeDefined();
});

it("displays the download failed button inside the failure messages dialog", async () => {
  const downloadButtonText = `Download ${FAILED} samples that failed sequencing`;

  const { queryByRole } = render(SequencingStatus, {
    sequencingStatus: {
      received: RECEIVED,
      completed: RECEIVED,
      failed: FAILED,
    },
  });

  expect(queryByRole("button", { name: downloadButtonText }))
    .toBeNull();

  await fireEvent.click(queryByRole("button", { name: "Show failed" }));

  expect(queryByRole("button", { name: downloadButtonText }))
    .toBeDefined();
});

it("displays the button to show failed sample sequencing", () => {
  const { getByRole } = render(SequencingStatus, {
    sequencingStatus: {
      received: RECEIVED,
      completed: RECEIVED,
      failed: FAILED
    },
  });

  expect(getByRole("button", { name: "Show failed" }))
    .toBeDefined();
});
