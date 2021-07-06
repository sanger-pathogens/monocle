import { render } from "@testing-library/svelte";
import InstitutionStatus from "./_InstitutionStatus.svelte";

const INSTITUTION_NAME = "Welfare Biology Research Institute";

it("displays an institution name", () => {
  const { getByText } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] }
  });

  expect(getByText(INSTITUTION_NAME)).toBeDefined();
});

it("displays a batch pane", () => {
  const samplesReceived = 42;

  const { container } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: samplesReceived, deliveries: [] }
  });

  expect(container.querySelectorAll("h4")[1].textContent)
    .toBe(`${samplesReceived} Samples Received`);
});

it("displays only an institution name and a short message when no samples received", () => {
  const { container, getByText } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 0, deliveries: [] }
  });

  const innerElements = container.querySelector("article").children;
  expect(innerElements).toHaveLength(2);
  expect(getByText(INSTITUTION_NAME)).toBeDefined();
  expect(getByText("No samples received")).toBeDefined();
});
