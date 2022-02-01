import { writable } from "svelte/store";

// FIXME unit test
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
