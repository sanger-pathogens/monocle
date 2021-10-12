import { render } from "@testing-library/svelte";
import { setContext } from "svelte";
import InstitutionStatus from "./_InstitutionStatus.svelte";

const INSTITUTION_NAME = "Welfare Biology Research Institute";
const ROLE_HEADING = "heading";

jest.mock("svelte", () => ({
  ...jest.requireActual("svelte"),
  setContext: jest.fn()
}));

it("displays an institution name", () => {
  const { getByRole } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  });

  expect(getByRole(ROLE_HEADING, { name: INSTITUTION_NAME }))
    .toBeDefined();
});

it("puts an institution's name into context", () => {
  render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  });

  expect(setContext).toHaveBeenCalledWith("institutionName", INSTITUTION_NAME);
});

it("displays only an institution name and a short message when no samples received", () => {
  const { container, getByText } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 0, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  });

  const innerElements = container.querySelector("article").children;
  expect(innerElements).toHaveLength(2);
  expect(getByText(INSTITUTION_NAME)).toBeDefined();
  expect(getByText("No samples received")).toBeDefined();
});

it.each([
  ["batch", / Samples Received$/ ],
  ["sequencing status", / Samples Sequenced$/ ],
  ["pipeline status", / Sample Pipelines Completed$/ ]
])("displays %s pane", (paneName, expectedHeadingText) => {
  const { getByRole } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  });

  expect(getByRole(ROLE_HEADING, { name: expectedHeadingText }))
    .toBeDefined();
});

it("displays the bulk download link", () => {
  const { getByRole } = render(InstitutionStatus, {
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {}
  });

  expect(getByRole("link", { name: "Bulk data download" }))
    .toBeDefined();
});
