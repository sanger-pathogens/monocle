import { fireEvent, render } from "@testing-library/svelte";
import SequencingStatus from "./_SequencingStatus.svelte";

const LANES_FAILED = 2;
const SAMPLES_RECEIVED = 10;

it("displays data passed", () => {
  const samplesCompleted = 8;

  const { container, getByText } = render(SequencingStatus, {
    sequencingStatus: {
      samples_received: SAMPLES_RECEIVED,
      samples_completed: samplesCompleted,
    },
  });

  expect(container.querySelector("h3").textContent).toBe(
    `${samplesCompleted} of ${SAMPLES_RECEIVED} Samples Sequenced`
  );
  expect(getByText("% completed", { exact: false })).toBeDefined();
});

it("displays a special heading when all samples are sequenced", () => {
  const { container } = render(SequencingStatus, {
    sequencingStatus: {
      samples_received: SAMPLES_RECEIVED,
      samples_completed: SAMPLES_RECEIVED,
    },
  });

  expect(container.querySelector("h3").textContent).toBe(
    `All ${SAMPLES_RECEIVED} Samples Sequenced`
  );
});

it("displays the download button", () => {
  const lanesSuccessful = SAMPLES_RECEIVED - LANES_FAILED;

  const { getByRole } = render(SequencingStatus, {
    sequencingStatus: {
      samples_received: SAMPLES_RECEIVED,
      samples_completed: SAMPLES_RECEIVED,
      lanes_successful: lanesSuccessful,
    },
  });

  expect(
    getByRole("button", {
      name: `Download metadata for ${lanesSuccessful} successfully sequenced samples`,
    })
  ).toBeDefined();
});

it("displays the download failed button inside the failure messages dialog", async () => {
  const downloadButtonText = `Download metadata for ${LANES_FAILED} samples that failed sequencing`;

  const { getByRole, queryByRole } = render(SequencingStatus, {
    sequencingStatus: {
      samples_received: SAMPLES_RECEIVED,
      samples_completed: SAMPLES_RECEIVED,
      lanes_failed: LANES_FAILED,
    },
  });

  expect(queryByRole("button", { name: downloadButtonText })).toBeNull();

  await fireEvent.click(queryByRole("button", { name: "Show failed" }));

  expect(getByRole("button", { name: downloadButtonText })).toBeDefined();
});

it("displays the button to show failed sample sequencing", () => {
  const { getByRole } = render(SequencingStatus, {
    sequencingStatus: {
      samples_received: SAMPLES_RECEIVED,
      samples_completed: SAMPLES_RECEIVED,
      lanes_failed: LANES_FAILED,
    },
  });

  expect(getByRole("button", { name: "Show failed" })).toBeDefined();
});
