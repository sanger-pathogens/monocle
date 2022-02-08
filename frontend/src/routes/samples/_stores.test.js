import { get } from "svelte/store";
import { distinctColumnValuesStore, filterStore } from "./_stores.js";

const VALUES = ["some value", "another value"];

it("has the expected default value for each store", () => {
  expect(get(distinctColumnValuesStore)).toEqual(
    { metadata: {}, "in silico": {}, "qc data": {} });
  expect(get(filterStore)).toEqual(
    { metadata: {}, "in silico": {}, "qc data": {} });
});

describe("distinct column values store", () => {
  it("doesn't expose `set` function", () => {
    expect(distinctColumnValuesStore.set).toBeUndefined();
  });

  it("doesn't expose `update` function", () => {
    expect(distinctColumnValuesStore.update).toBeUndefined();
  });

  it("can update values from a distinct values response", () => {
    distinctColumnValuesStore.updateFromDistinctValuesResponse([{
      "field type": "metadata",
      fields: [{ name: "country", values: VALUES }]
    }, {
      "field type": "metadata",
      fields: [{ name: "serotype", values: [] }]
    }, {
      "field type": "qc data",
      fields: [{ name: "rel_abun_sa", values: VALUES }]
    }]);

    expect(get(distinctColumnValuesStore)).toEqual({
      metadata: { country: VALUES, serotype: [] },
      "qc data": { rel_abun_sa: VALUES },
      "in silico": {}
    });
  });
});

describe("filter store", () => {
  it("exposes a function to remove all filters", () => {
    filterStore.set({ someKey: VALUES[0] });

    filterStore.removeAllFilters();

    expect(get(filterStore)).toEqual(
      { metadata: {}, "in silico": {}, "qc data": {} });
  });

  it("exposes a function to remove a filter for a given column", () => {
    const columnDataType = "in silico";
    const columnName = "some column";
    const metadataFilter = { metadata: { anotherColumn: [VALUES[0]] } };
    const filters = {
      ...metadataFilter
    };
    filters[columnDataType] = { anotherInSilicoColumn: [VALUES[0]] };
    filters[columnDataType][columnName] = [VALUES[0]];
    filterStore.set(filters);

    filterStore.removeFilter({ name: columnName, dataType: columnDataType });

    expect(get(filterStore)).toEqual({
      [columnDataType]: { anotherInSilicoColumn: [VALUES[0]] },
      ...metadataFilter
    });
  })
});
