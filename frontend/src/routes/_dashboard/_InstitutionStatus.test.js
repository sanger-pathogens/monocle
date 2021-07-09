import { render } from "@testing-library/svelte";
import InstitutionStatus from "./_InstitutionStatus.svelte";

const INSTITUTION_NAME = "Welfare Biology Research Institute";
const ROLE_HEADING = "heading";

it("displays an institution name", () => {
  const { getByText } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {}
  });

  expect(getByText(INSTITUTION_NAME)).toBeDefined();
});

it("displays the batch pane", () => {
  const { queryByRole } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {}
  });

  expect(queryByRole(ROLE_HEADING, { name: / Samples Received$/ }))
    .toBeTruthy();
});

it("displays the sequencing status pane", () => {
  const { queryByRole } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {}
  });

  expect(queryByRole(ROLE_HEADING, { name: / Samples Sequenced$/ }))
    .toBeTruthy();
});

it("displays only an institution name and a short message when no samples received", () => {
  const { container, getByText } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 0, deliveries: [] },
    sequencingStatus: {}
  });

  const innerElements = container.querySelector("article").children;
  expect(innerElements).toHaveLength(2);
  expect(getByText(INSTITUTION_NAME)).toBeDefined();
  expect(getByText("No samples received")).toBeDefined();
});
