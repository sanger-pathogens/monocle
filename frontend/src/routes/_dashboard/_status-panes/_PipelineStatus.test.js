import { fireEvent, render } from "@testing-library/svelte";
import PipelineStatus from "./_PipelineStatus.svelte";

const FAILED = 2;
const SEQUENCED_SUCCESS = 10;

it("displays data passed", () => {
  const completed = SEQUENCED_SUCCESS - FAILED;

  const { container, getByText } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: SEQUENCED_SUCCESS,
      completed
    },
  });

  expect(container.querySelector("h3").textContent)
    .toBe(`${completed} of ${SEQUENCED_SUCCESS} Sample Pipelines Completed`);
  expect(getByText("% completed", { exact: false }))
    .toBeDefined();
});

it("displays a special heading when all pipelines are finished", () => {
  const { container } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: SEQUENCED_SUCCESS,
      completed: SEQUENCED_SUCCESS
    },
  });

  expect(container.querySelector("h3").textContent)
    .toBe(`All ${SEQUENCED_SUCCESS} Sample Pipelines Completed`);
});

it("displays only a heading if there are no pipelines", () => {
  const { getByRole } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: 0
    },
  });

  const headingElement = getByRole("heading", { name: "No Pipelines Started" });
  expect(headingElement).toBeDefined();
  const paneContent = headingElement.parentNode.children;
  expect(paneContent).toHaveLength(1);
});

it("displays the download button", () => {
  const succeeded = SEQUENCED_SUCCESS - FAILED;

  const { getByRole } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: SEQUENCED_SUCCESS,
      completed: SEQUENCED_SUCCESS,
      success: succeeded,
    },
  });

  expect(getByRole("button", { name: `Download metadata for ${succeeded} samples successfully processed through the pipeline` }))
    .toBeDefined();
});

it("displays the download failed button inside the failure messages dialog", async () => {
  const downloadButtonText = `Download metadata for ${FAILED} samples that failed processing through the pipeline`;

  const { getByRole, queryByRole } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: SEQUENCED_SUCCESS,
      completed: SEQUENCED_SUCCESS,
      failed: FAILED,
    },
  });

  expect(queryByRole("button", { name: downloadButtonText }))
    .toBeNull();

  await fireEvent.click(queryByRole("button", { name: "Show failed" }));

  expect(getByRole("button", { name: downloadButtonText }))
    .toBeDefined();
});

it("displays the button to show failed pipelines", () => {
  const { getByRole } = render(PipelineStatus, {
    pipelineStatus: {
      sequencedSuccess: SEQUENCED_SUCCESS,
      completed: SEQUENCED_SUCCESS,
      failed: FAILED
    },
  });

  expect(getByRole("button", { name: "Show failed" }))
    .toBeDefined();
});

