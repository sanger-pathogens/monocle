import { get } from "svelte/store";
import {
  columnsStore, columnsToDisplayStore, distinctColumnValuesStore, filterStore } from "./_stores.js";

const INITIAL_STATE = { metadata: {}, "in silico": {}, "qc data": {} };
const VALUES = ["some value", "another value"];

it("has the expected default value for each store", () => {
  expect(get(columnsStore)).toBeUndefined();
  expect(get(columnsToDisplayStore)).toBeUndefined();
  expect(get(distinctColumnValuesStore)).toEqual(INITIAL_STATE);
  expect(get(filterStore)).toEqual(INITIAL_STATE);
});

it("has a derived store w/ an array of columns per data type to display", () => {
  columnsStore.set({
    metadata: [{ name: "Category A", columns: [
      { displayName: "Country", name: "country", selected: true }, { displayName: "Study Reference", name: "study_ref" }] }],
    "in silico": [{ name: "Category B", columns: [{ displayName: "ST", name: "st", selected: true }] }]
  });

  expect(get(columnsToDisplayStore)).toEqual({
    metadata: ["country"], "in silico": ["st"]
  });
});

describe("columns store", () => {
  it("doesn't expose `update` function", () => {
    expect(columnsStore.update).toBeUndefined();
  });

  it("can be set from the columns response", () => {
    columnsStore.setFromColumnsResponse({
      metadata: { categories: [{
        name: "Category A",
        fields: [{ name: "a", display: false }, { "display name": "Country", name: "country", display: true }]
      }] },
      "in silico": { categories: [{
        name: "Category B",
        fields: [{ "display name": "C", name: "c", display: true, "filter type": "discrete" }]
      }, {
        name: "Category C",
        fields: [{ name: "d", display: false }]
      }] }
    });

    expect(get(columnsStore)).toEqual({
      metadata: [{ name: "Category A", columns: [{ displayName: "Country", name: "country", selected: true }] }],
      "in silico": [{ name: "Category B", columns: [{ displayName: "C", name: "c", type: "discrete" }] }]
    });
  });

  it("can reset the state to the default", () => {
    columnsStore.set({
      metadata: [{ name: "Category A", columns: [
        { displayName: "Country", name: "country" }, { displayName: "Study Reference", name: "study_ref", selected: true }] }],
      "in silico": [{ name: "Category B", columns: [{ displayName: "ST", name: "st", type: "discrete" }] }]
    });

    columnsStore.setToDefault();

    expect(get(columnsStore)).toEqual({
      metadata: [{ name: "Category A", columns: [
        { displayName: "Country", name: "country", selected: true }, { displayName: "Study Reference", name: "study_ref", selected: false }] }],
      "in silico": [{ name: "Category B", columns: [{ displayName: "ST", name: "st", type: "discrete", selected: undefined }] }]
    });
  });
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
      fields: [{ name: "country", matches: [{ number: 0, value: VALUES[0] }, { number: 3, value: VALUES[1] }] }]
    }, {
      "field type": "metadata",
      fields: [{ name: "serotype", matches: [] }]
    }, {
      "field type": "qc data",
      fields: [{ name: "rel_abun_sa", matches: [{ number: 5, value: VALUES[0] }, { number: 3, value: VALUES[1] }] }]
    }]);

    expect(get(distinctColumnValuesStore)).toEqual({
      metadata: { country: [VALUES[1]], serotype: [] },
      "qc data": { rel_abun_sa: VALUES },
      "in silico": {}
    });
  });

  it("can reset state", () => {
    distinctColumnValuesStore.updateFromDistinctValuesResponse([{
      "field type": "metadata",
      fields: [{ name: "country", matches: [{ number: 0, value: VALUES[0] }, { number: 3, value: VALUES[1] }] }]}]);

    distinctColumnValuesStore.reset();

    expect(get(distinctColumnValuesStore)).toEqual(INITIAL_STATE);
  });
});

describe("filter store", () => {
  it("exposes a function to remove all filters", () => {
    filterStore.set({ someKey: VALUES[0] });

    filterStore.removeAllFilters();

    expect(get(filterStore)).toEqual(INITIAL_STATE);
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
  });
});
