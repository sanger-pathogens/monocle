import { render } from "@testing-library/svelte";
import PipelineStatus from "./_PipelineStatus.svelte";

it("displays data passed", () => {
  const sequencedSuccess = 30;
  const completed = 10;

  const { container, getByText } = render(PipelineStatus, { pipelineStatus: {
    sequencedSuccess,
    completed
  }});

  expect(container.querySelector("h4").textContent)
    .toBe(`${completed} of ${sequencedSuccess} Sample Pipelines Completed`);
  expect(getByText("% completed", { exact: false }))
    .toBeDefined();
});

it("displays a special heading when all pipelines are finished", () => {
  const sequencedSuccess = 30;

  const { container } = render(PipelineStatus, { pipelineStatus: {
    sequencedSuccess,
    completed: sequencedSuccess
  }});

  expect(container.querySelector("h4").textContent)
    .toBe(`All ${sequencedSuccess} Sample Pipelines Completed`);
});

it("displays only a heading if there are no pipelines", () => {
  const { getByRole } = render(PipelineStatus, { pipelineStatus: {
    sequencedSuccess: 0
  }});

  const headingElement = getByRole("heading", { name: "No Pipelines Started" });
  expect(headingElement).toBeDefined();
  const paneContent = headingElement.parentNode.children;
  expect(paneContent).toHaveLength(1);
});

