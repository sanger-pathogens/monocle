import { get } from "svelte/store";
import { distinctColumnValuesStore, filterStore } from "./_stores.js";

it("has the expected default value for each store", () => {
  expect(get(distinctColumnValuesStore)).toEqual(
    { metadata: {}, "in silico": {}, "qc data": {} });
  expect(get(filterStore)).toEqual(
    { metadata: {}, "in silico": {}, "qc data": {} });
});

describe("filter store", () => {
  const VALUE = "some value";

  it("exposes a function to remove all filters", () => {
    filterStore.set({ someKey: VALUE });

    filterStore.removeAllFilters();

    expect(get(filterStore)).toEqual(
      { metadata: {}, "in silico": {}, "qc data": {} });
  });

  it("exposes a function to remove a filter for a given column", () => {
    const columnDataType = "in silico";
    const columnName = "some column";
    const metadataFilter = { metadata: { anotherColumn: [VALUE] } };
    const filters = {
      ...metadataFilter
    };
    filters[columnDataType] = { anotherInSilicoColumn: [VALUE] };
    filters[columnDataType][columnName] = [VALUE];
    filterStore.set(filters);

    filterStore.removeFilter({ name: columnName, dataType: columnDataType });

    expect(get(filterStore)).toEqual({
      [columnDataType]: { anotherInSilicoColumn: [VALUE] },
      ...metadataFilter
    });
  })
});
