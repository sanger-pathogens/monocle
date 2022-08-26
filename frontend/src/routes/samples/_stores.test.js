import { get } from "svelte/store";
import {
  columnsStore,
  displayedColumnNamesStore,
  displayedColumnsStore,
  distinctColumnValuesStore,
  filterStore,
} from "./_stores.js";

const COLUMNS_STATE = {
  metadata: [
    {
      name: "Category A",
      columns: [
        { displayName: "Country", name: "country", selected: true },
        { displayName: "Study Reference", name: "study_ref" },
      ],
    },
  ],
  "qc data": [
    {
      name: "Category C",
      columns: [{ displayName: "E", name: "e", selected: true }],
    },
  ],
  "in silico": [
    {
      name: "Category B",
      columns: [{ displayName: "ST", name: "st", selected: true }],
    },
  ],
};
const INITIAL_STATE = { metadata: {}, "qc data": {}, "in silico": {} };
const VALUES = ["some value", "another value"];

it("has the expected default value for each store", () => {
  expect(get(columnsStore)).toBeUndefined();
  expect(get(displayedColumnNamesStore)).toBeUndefined();
  expect(get(displayedColumnsStore)).toBeUndefined();
  expect(get(distinctColumnValuesStore)).toEqual(INITIAL_STATE);
  expect(get(filterStore)).toEqual(INITIAL_STATE);
});

it("has a derived store w/ an array of column names per data type to display", () => {
  columnsStore.set(COLUMNS_STATE);

  expect(get(displayedColumnNamesStore)).toEqual({
    metadata: ["country"],
    "qc data": ["e"],
    "in silico": ["st"],
  });
});

it("has a derived store w/ an array of columns per data type to display", () => {
  columnsStore.set(COLUMNS_STATE);

  expect(get(displayedColumnsStore)).toEqual({
    metadata: [{ displayName: "Country", name: "country", selected: true }],
    "qc data": [{ displayName: "E", name: "e", selected: true }],
    "in silico": [{ displayName: "ST", name: "st", selected: true }],
  });
});

describe("columns store", () => {
  it("doesn't expose `update` function", () => {
    expect(columnsStore.update).toBeUndefined();
  });

  it("can be set from the columns response", () => {
    columnsStore.setFromColumnsResponse({
      metadata: {
        categories: [
          {
            name: "Category A",
            fields: [
              { name: "a", display: false },
              {
                "display name": "Country",
                name: "country",
                display: true,
                default: true,
              },
            ],
          },
        ],
      },
      "qc data": {
        categories: [
          {
            name: "Category D",
            fields: [
              {
                "display name": "X",
                name: "x",
                display: true,
                default: false,
                "filter type": "discrete",
              },
            ],
          },
        ],
      },
      "in silico": {
        categories: [
          {
            name: "Category B",
            fields: [
              {
                "display name": "C",
                name: "c",
                display: true,
                default: false,
                "filter type": "discrete",
              },
            ],
          },
          {
            name: "Category C",
            fields: [{ name: "d", display: false }],
          },
        ],
      },
    });

    expect(get(columnsStore)).toEqual({
      metadata: [
        {
          name: "Category A",
          columns: [
            {
              displayName: "Country",
              name: "country",
              default: true,
              selected: true,
            },
          ],
        },
      ],
      "qc data": [
        {
          name: "Category D",
          columns: [{ displayName: "X", name: "x", type: "discrete" }],
        },
      ],
      "in silico": [
        {
          name: "Category B",
          columns: [{ displayName: "C", name: "c", type: "discrete" }],
        },
      ],
    });
  });

  it("can reset the state to default columns", () => {
    columnsStore.set({
      metadata: [
        {
          name: "Category A",
          columns: [
            { displayName: "Country", name: "country", default: true },
            {
              displayName: "Study Reference",
              name: "study_ref",
              selected: true,
            },
          ],
        },
      ],
      "in silico": [
        {
          name: "Category B",
          columns: [{ displayName: "ST", name: "st", type: "discrete" }],
        },
      ],
    });

    columnsStore.setToDefault();

    expect(get(columnsStore)).toEqual({
      metadata: [
        {
          name: "Category A",
          columns: [
            {
              displayName: "Country",
              name: "country",
              default: true,
              selected: true,
            },
            {
              displayName: "Study Reference",
              name: "study_ref",
              selected: undefined,
            },
          ],
        },
      ],
      "in silico": [
        {
          name: "Category B",
          columns: [
            {
              displayName: "ST",
              name: "st",
              type: "discrete",
              selected: undefined,
            },
          ],
        },
      ],
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
    distinctColumnValuesStore.updateFromDistinctValuesResponse([
      {
        "field type": "metadata",
        fields: [
          {
            name: "country",
            matches: [
              { number: 0, value: VALUES[0] },
              { number: 3, value: VALUES[1] },
            ],
          },
        ],
      },
      {
        "field type": "metadata",
        fields: [{ name: "serotype", matches: [] }],
      },
    ]);

    expect(get(distinctColumnValuesStore)).toEqual({
      metadata: { country: [VALUES[1]], serotype: [] },
      "qc data": {},
      "in silico": {},
    });
  });

  it("can reset state", () => {
    distinctColumnValuesStore.updateFromDistinctValuesResponse([
      {
        "field type": "metadata",
        fields: [
          {
            name: "country",
            matches: [
              { number: 0, value: VALUES[0] },
              { number: 3, value: VALUES[1] },
            ],
          },
        ],
      },
    ]);

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
      ...metadataFilter,
    };
    filters[columnDataType] = { anotherInSilicoColumn: [VALUES[0]] };
    filters[columnDataType][columnName] = [VALUES[0]];
    filterStore.set(filters);

    filterStore.removeFilter({ name: columnName, dataType: columnDataType });

    expect(get(filterStore)).toEqual({
      [columnDataType]: { anotherInSilicoColumn: [VALUES[0]] },
      ...metadataFilter,
    });
  });
});
