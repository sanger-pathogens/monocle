import { writable } from "svelte/store";


export const distinctColumnValuesStore = writable({ metadata: {}, "in silico": {}, "qc data": {} });


function createFilterStore() {
  const filterCustomStore = writable({ metadata: {}, "in silico": {}, "qc data": {} });

  filterCustomStore.removeAllFilters = () => filterCustomStore.set(
    { metadata: {}, "in silico": {}, "qc data": {} });

  filterCustomStore.removeFilter = (column) => filterCustomStore.update((filters) => {
    delete filters[column.dataType][column.name];
    return filters;
  });

  return filterCustomStore;
}

export const filterStore = createFilterStore();
