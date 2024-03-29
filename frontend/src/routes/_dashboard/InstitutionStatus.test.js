import { render } from "@testing-library/svelte";
import { setContext } from "svelte";
import InstitutionStatus from "./InstitutionStatus.svelte";

const API_ERROR = "some error";
const INSTITUTION_KEY = "WelBioResIns";
const INSTITUTION_NAME = "Welfare Biology Research Institute";
const RE_STATUS_PANE_HEADING_TEXT =
  / (?:Samples (?:Received|Sequenced))|(?:Pipelines Completed)$/;
const ROLE_HEADING = "heading";

jest.mock("svelte", () => ({
  ...jest.requireActual("svelte"),
  setContext: jest.fn(),
}));

it("displays an institution name", () => {
  const { getByRole } = render(InstitutionStatus, {
    institutionKey: INSTITUTION_KEY,
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {},
  });

  expect(getByRole(ROLE_HEADING, { name: INSTITUTION_NAME })).toBeDefined();
});

it("puts an institution's name into context", () => {
  render(InstitutionStatus, {
    institutionKey: INSTITUTION_KEY,
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {},
  });

  expect(setContext).toHaveBeenCalledWith("institutionKey", INSTITUTION_KEY);
});

it("displays only an institution name and a short message when no samples received", () => {
  const { container, getByRole, getByText } = render(InstitutionStatus, {
    institutionKey: INSTITUTION_KEY,
    institutionName: INSTITUTION_NAME,
    batches: { received: 0, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {},
  });

  const innerElements = container.querySelector("article").children;
  expect(innerElements).toHaveLength(2);
  expect(getByRole(ROLE_HEADING, { name: INSTITUTION_NAME })).toBeDefined();
  expect(getByText("No samples received")).toBeDefined();
});

it.each([
  ["batch", / Samples Received$/],
  ["sequencing status", / Samples Sequenced$/],
  ["pipeline status", / Pipelines Completed$/],
])("displays %s pane", (paneName, expectedHeadingText) => {
  const { getByRole } = render(InstitutionStatus, {
    institutionKey: INSTITUTION_KEY,
    institutionName: INSTITUTION_NAME,
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {},
  });

  expect(getByRole(ROLE_HEADING, { name: expectedHeadingText })).toBeDefined();
});

it.each([
  [
    "batch",
    {
      batches: { _ERROR: API_ERROR },
      sequencingStatus: {},
      pipelineStatus: {},
    },
  ],
  [
    "sequencing status",
    {
      batches: {},
      sequencingStatus: { _ERROR: API_ERROR },
      pipelineStatus: {},
    },
  ],
  [
    "pipeline status",
    {
      batches: {},
      sequencingStatus: {},
      pipelineStatus: { _ERROR: API_ERROR },
    },
  ],
])(
  "displays an institution name and an API error if %s response has the error field",
  (endpointName, props) => {
    const { getByRole, getByText, queryByRole } = render(InstitutionStatus, {
      institutionKey: INSTITUTION_KEY,
      institutionName: INSTITUTION_NAME,
      ...props,
    });

    expect(getByRole(ROLE_HEADING, { name: INSTITUTION_NAME })).toBeDefined();
    expect(getByText(`⚠️ ${API_ERROR}`)).toBeDefined();
    expect(
      queryByRole(ROLE_HEADING, { name: { RE_STATUS_PANE_HEADING_TEXT } })
    ).toBeNull();
  }
);
