import { render } from "@testing-library/svelte";
import SequencingStatus from "./_SequencingStatus.svelte";

const INSTITUTION = "Invincible Wellbeing";

it("displays data passed", () => {
  const received = 30;
  const completed = 10;

  const { container, getByText } = render(SequencingStatus, {
    sequencingStatus: {
      received,
      completed
    },
    institutionName: INSTITUTION
  });

  expect(container.querySelector("h4").textContent)
    .toBe(`${completed} of ${received} Samples Sequenced`);
  expect(getByText("% completed", { exact: false }))
    .toBeDefined();
});

it("displays a special heading when all samples are sequenced", () => {
  const received = 30;

  const { container } = render(SequencingStatus, {
    sequencingStatus: {
      received,
      completed: received
    },
    institutionName: INSTITUTION
  });

  expect(container.querySelector("h4").textContent)
    .toBe(`All ${received} Samples Sequenced`);
});

it("displays the download buttons", () => {
  const succeeded = 8;
  const failed = 2;

  const { getByRole } = render(SequencingStatus, {
    sequencingStatus: {
      received: 10,
      completed: 10,
      success: succeeded,
      failed
    },
    institutionName: INSTITUTION
  });

  expect(getByRole("button", { name: `Download ${succeeded} successfully sequenced samples` }))
    .toBeDefined();
  expect(getByRole("button", { name: `Download ${failed} samples that failed sequencing` }))
    .toBeDefined();
});

