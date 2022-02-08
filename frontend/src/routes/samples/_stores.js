import { writable } from "svelte/store";


/*
  `distinctColumnValuesStore` has the following shape:
  ```
    {
      metadata: {
        columnName1: ["val1", "val2"],
        columnName2: ["val1", "val2"]
      },
      "in silico": {
        columnName3: ["val1", "val2"],
        columnName4: ["val1", "val2"]
      },
      "qc data": {
        columnName5: ["val1", "val2"],
        columnName6: ["val1", "val2"]
      }
    }
  ```
*/
function createDistinctColumnValuesStore() {
  const { update, subscribe } = writable({ metadata: {}, "in silico": {}, "qc data": {} });

  return {
    subscribe,
    updateFromDistinctValuesResponse: (distinctValuesResponse) => update((storedDistinctValues) => {
      distinctValuesResponse.forEach(({ "field type": dataType, fields: columns }) =>
        columns.forEach((column) =>
          storedDistinctValues[dataType][column.name] = column.values));

      return storedDistinctValues;
    })
  };
}

export const distinctColumnValuesStore = createDistinctColumnValuesStore();


/*
  `filterStore` has the following shape:
  ```
    {
      metadata: {
        columnName1: { values: ["val1", "val2"], exclude: true },
        columnName2: { values: ["val1", "val2"] },
      },
      "in silico": {
        columnName3: { values: ["val1", "val2"] },
        columnName4: { values: ["val1", "val2"], exclude: true },
      },
      "qc data": {
        columnName5: { values: ["val1", "val2"], exclude: true },
        columnName6: { values: ["val1", "val2"], exclude: true },
      }
    }
  ```
*/
function createFilterStore() {
  const filterCustomStore = writable({ metadata: {}, "in silico": {}, "qc data": {} });

  filterCustomStore.removeAllFilters = () => filterCustomStore.set(
    { metadata: {}, "in silico": {}, "qc data": {} });

  filterCustomStore.removeFilter = (column) => filterCustomStore.update((stotedFilters) => {
    delete stotedFilters[column.dataType][column.name];
    return stotedFilters;
  });

  return filterCustomStore;
}

export const filterStore = createFilterStore();
