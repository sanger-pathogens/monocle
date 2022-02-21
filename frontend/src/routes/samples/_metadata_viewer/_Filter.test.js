import { fireEvent, render } from "@testing-library/svelte";
import { get } from "svelte/store";
import { distinctColumnValuesStore, filterStore } from "../_stores.js";
import Filter from "./_Filter.svelte";
import { getDistinctColumnValues } from "$lib/dataLoading.js";

jest.mock("$lib/dataLoading.js", () => ({
  getDistinctColumnValues: jest.fn(() => Promise.resolve([{
    "field type": "metadata",
    fields: [{ name: "serotype", matches: [{ number: 1, value: "1a" }, { number: 3, value: "1b" }] }]
  }]))
}));

const BATCHES = [];
const CLASS_NAME_VALUE_SELECTOR = "selectContainer";
const DATA_TYPE_METADATA = "metadata";
const COLUMN = { title: "Serotype", name: "serotype", dataType: DATA_TYPE_METADATA };
const DISTINCT_VALUES = ["1a", "1b"];
const LABEL_BUTTON_APPLY = "Apply";
const LABEL_BUTTON_APPLY_AND_CLOSE = "Apply and close";
const LABEL_EXCLUDE = "Exclude samples with the selected values";
const ROLE_BUTTON = "button";

afterEach(() => {
  distinctColumnValuesStore.reset();
});

it("has a column name in the heading", () => {
  const { getByRole } = render(Filter, { batches: BATCHES, column: COLUMN });

  expect(getByRole("heading", { name: `Filter samples by ${COLUMN.title}` }))
    .toBeDefined();
});

it("fetches and displays column values if there are no stored values", async () => {
  getDistinctColumnValues.mockClear();
  const { container, getByText } = render(Filter, { batches: BATCHES, column: COLUMN });

  await fireEvent.click(container.getElementsByClassName(CLASS_NAME_VALUE_SELECTOR)[0]);

  expect(getDistinctColumnValues).toHaveBeenCalledTimes(1);
  expect(getDistinctColumnValues).toHaveBeenCalledWith({
    instKeyBatchDatePairs: BATCHES,
    columns: [COLUMN],
    filter: { filterState: get(filterStore), distinctColumnValues: get(distinctColumnValuesStore) },
  }, fetch);
  DISTINCT_VALUES.forEach((value) =>
    expect(getByText(value)).toBeDefined());
});

it("displays stored column values instead of fetching new ones", async () => {
  const alternativeDistinctValues = ["a42", "b42"];
  getDistinctColumnValues.mockClear();
  distinctColumnValuesStore.updateFromDistinctValuesResponse([{
    "field type": DATA_TYPE_METADATA,
    fields: [{ name: COLUMN.name, matches:
      [{ number: 9, value: alternativeDistinctValues[0] }, { number: 9, value: alternativeDistinctValues[1] }]}]
  }]);
  const { container, getByText } = render(Filter, { batches: BATCHES, column: COLUMN });

  await fireEvent.click(queryValueSelectorElement(container));

  expect(getDistinctColumnValues).not.toHaveBeenCalled();
  alternativeDistinctValues.forEach((value) =>
    expect(getByText(value)).toBeDefined());
});

it("enables the apply buttons if there's a difference between values selected and ones of the active filter", async () => {
  setActiveFilter();
  const { container, getByRole, getByText } = render(Filter, { batches: BATCHES, column: COLUMN });
  const valueSelector = queryValueSelectorElement(container);
  await fireEvent.click(valueSelector);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }).disabled)
    .toBeTruthy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY }).disabled)
    .toBeTruthy();

  await fireEvent.click(getByText(DISTINCT_VALUES[1]));

  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }).disabled)
    .toBeFalsy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY }).disabled)
    .toBeFalsy();

  const secondValueRemovalButton = valueSelector.querySelectorAll("[class*=clear]")[1];
  await fireEvent.click(secondValueRemovalButton);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }).disabled)
    .toBeTruthy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY }).disabled)
    .toBeTruthy();

  filterStore.removeAllFilters();
});

it("enables the apply buttons if selected values and one in the active filter are the same but the exclusion mode is different", async () => {
  setActiveFilter();
  const { getByLabelText, getByRole } = render(Filter, { batches: BATCHES, column: COLUMN });

  const exclusionCheckbox = getByLabelText(LABEL_EXCLUDE);
  await fireEvent.click(exclusionCheckbox);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }).disabled)
    .toBeFalsy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY }).disabled)
    .toBeFalsy();

  await fireEvent.click(exclusionCheckbox);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }).disabled)
    .toBeTruthy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY }).disabled)
    .toBeTruthy();

  filterStore.removeAllFilters();
});

it("keeps the apply buttons disabled if the exclusion checkbox is toggled while no values are selected", async () => {
  const { getByLabelText, getByRole } = render(Filter, { batches: BATCHES, column: COLUMN });

  const exclusionCheckbox = getByLabelText(LABEL_EXCLUDE);
  await fireEvent.click(exclusionCheckbox);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }).disabled)
    .toBeTruthy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY }).disabled)
    .toBeTruthy();
});

it("closes the filter if the \"apply and close\" button is clicked", async () => {
  setActiveFilter();
  const { container, getByLabelText, getByRole } = render(Filter, { batches: BATCHES, column: COLUMN });
  await fireEvent.click(getByLabelText(LABEL_EXCLUDE));

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_BUTTON_APPLY_AND_CLOSE }));

  expect(container.innerHTML).toBe("<div></div>");

  filterStore.removeAllFilters();
});

it("closes the filter if the close button is clicked", async () => {
  const { container, getByRole } = render(Filter, { batches: BATCHES, column: COLUMN });

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: "Close" }));

  expect(container.innerHTML).toBe("<div></div>");
});

it("removes an active filter on clicking the removal button and disables the button", async () => {
  const labelFilterRemovalButton = `Remove the filter for column ${COLUMN.title}`;
  setActiveFilter();
  const { getByLabelText } = render(Filter, { batches: BATCHES, column: COLUMN });

  await fireEvent.click(getByLabelText(labelFilterRemovalButton));

  expect(get(filterStore)[DATA_TYPE_METADATA][COLUMN.name])
    .toBeUndefined();
  expect(getByLabelText(labelFilterRemovalButton).disabled)
    .toBeTruthy();
});

function queryValueSelectorElement(container) {
  return container.getElementsByClassName(CLASS_NAME_VALUE_SELECTOR)[0] || null;
}

function setActiveFilter() {
  filterStore.update((filterState) => {
    filterState[DATA_TYPE_METADATA][COLUMN.name] = { values: [DISTINCT_VALUES[0]] };
    return filterState;
  });
}
