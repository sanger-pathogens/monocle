import { render } from "@testing-library/svelte";
import PipelineStatus from "./_PipelineStatus.svelte";

const INSTITUTION = "Sentience Institute";

it("displays data passed", () => {
  const sequencedSuccess = 30;
  const completed = 10;

  const { container, getByText } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess,
      completed
    },
    institutionName: INSTITUTION
  });

  expect(container.querySelector("h4").textContent)
    .toBe(`${completed} of ${sequencedSuccess} Sample Pipelines Completed`);
  expect(getByText("% completed", { exact: false }))
    .toBeDefined();
});

it("displays a special heading when all pipelines are finished", () => {
  const sequencedSuccess = 30;

  const { container } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess,
      completed: sequencedSuccess
    },
    institutionName: INSTITUTION
  });

  expect(container.querySelector("h4").textContent)
    .toBe(`All ${sequencedSuccess} Sample Pipelines Completed`);
});

it("displays only a heading if there are no pipelines", () => {
  const { getByRole } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: 0
    },
    institutionName: INSTITUTION
  });

  const headingElement = getByRole("heading", { name: "No Pipelines Started" });
  expect(headingElement).toBeDefined();
  const paneContent = headingElement.parentNode.children;
  expect(paneContent).toHaveLength(1);
});

it("displays the download buttons", () => {
  const succeeded = 8;
  const failed = 2;

  const { getByRole } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: 10,
      completed: 10,
      success: succeeded,
      failed
    },
    institutionName: INSTITUTION
  });

  expect(getByRole("button", { name: `Download ${succeeded} samples successfully processed through the pipeline` }))
    .toBeDefined();
  expect(getByRole("button", { name: `Download ${failed} samples that failed processing through the pipeline` }))
    .toBeDefined();
});
