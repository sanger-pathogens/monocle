import { derived, writable } from "svelte/store";
import { DATA_TYPES } from "$lib/constants.js";

const FILTER_TYPE_NONE = "none";

/*
  `columnsStore` has the following shape:
```
  {
    metadata: [{
      name: "Category Name",
      columns: [{
        displayName: "Column Name",
        name: "column_name",
        default?: true,
        selected?: true,
        type?: "numeric"
      }, {
        ...
      }]
    }, {
      ...
    }],
    "in silico": [...]
  }
```
*/
// IMPORTANT: when changing `columnsStore`, increment `$lib/constants/LOCAL_STORAGE_KEY_COLUMNS_STATE`.
function createColumnsStore() {
  const { set, update, subscribe } = writable();

  return {
    set,
    subscribe,
    setFromColumnsResponse: (columnsResponse) => set(convertColumnsResponseToState(columnsResponse)),
    setToDefault: () => update((columnsState) => {
      DATA_TYPES.forEach((dataType) =>
        columnsState[dataType].forEach((category) =>
          category.columns.forEach((column) =>
            column.selected = column.default)));
      return columnsState;
    })
  };
}

export const columnsStore = createColumnsStore();


/*
  `columnsToDisplayStore` has the following shape:
  ```
  {
    metadata: ["column_name_1", "column_name_2"],
    "in silico": [...]
  }
  ```
*/
export const columnsToDisplayStore = derived(columnsStore, (columnsState) =>
  columnsState ?
    Object.keys(columnsState).reduce((accumDataTypeToColumnNames, dataType) => {
      accumDataTypeToColumnNames[dataType] = columnsState[dataType].reduce(columnCategoryToColumnNamesReducer, []);
      return accumDataTypeToColumnNames;
    }, {}) :
    undefined);

function columnCategoryToColumnNamesReducer(accumColumnNames, category) {
  category.columns.forEach((column) => {
    if (column.selected) {
      accumColumnNames.push(column.name);
    }
  });
  return accumColumnNames;
}


/*
  `distinctColumnValuesStore` has the following shape:
  ```
    {
      metadata: {
        columnName1: ["val1", "val2"],
        columnName2: ["val1", "val2"]
      },
      "in silico": {...}
    }
  ```
*/
function createDistinctColumnValuesStore() {
  const { update, set, subscribe } = writable({ metadata: {}, "in silico": {} });

  return {
    subscribe,
    updateFromDistinctValuesResponse: (distinctValuesResponse) => update((storedDistinctValues) => {
      distinctValuesResponse.forEach(({ "field type": dataType, fields: columns }) =>
        columns.forEach((column) =>
          storedDistinctValues[dataType][column.name] = column.matches.reduce((accumValues, match) => {
            if (match.number) {
              accumValues.push(match.value);
            }
            return accumValues;
          }, [])));

      return storedDistinctValues;
    }),
    reset: () => set({ metadata: {}, "in silico": {} })
  };
}

export const distinctColumnValuesStore = createDistinctColumnValuesStore();


/*
  `filterStore` has the following shape:
  ```
    {
      metadata: {
        columnName1: { values: ["val1", "val2"], exclude?: true },
        columnName2: {...},
      },
      "in silico": {...}
    }
  ```
*/
function createFilterStore() {
  const filterCustomStore = writable({ metadata: {}, "in silico": {} });

  filterCustomStore.removeAllFilters = () => filterCustomStore.set(
    { metadata: {}, "in silico": {} });

  filterCustomStore.removeFilter = (column) => filterCustomStore.update((stotedFilters) => {
    delete stotedFilters[column.dataType][column.name];
    return stotedFilters;
  });

  return filterCustomStore;
}

export const filterStore = createFilterStore();


function convertColumnsResponseToState(columnsResponse) {
  return Object.keys(columnsResponse)
    .reduce((accumColumnsState, dataType) => {
      accumColumnsState[dataType] = transformCategoriesFromResponse(
        columnsResponse[dataType].categories);
      return accumColumnsState;
    }, {});
}

function transformCategoriesFromResponse(categories = []) {
  return categories.reduce((accumCategories, category) => {
    const convertedCategory = {
      name: category.name,
      columns: transformColumnsFromResponse(category.fields)
    };
    if (convertedCategory.columns.length) {
      accumCategories.push(convertedCategory);
    }
    return accumCategories;
  }, []);
}

function transformColumnsFromResponse(columns = []) {
  return columns.reduce((accumColumns, column) => {
    if (column.display) {
      const convertedColumn = {
        displayName: column["display name"],
        name: column.name
      };
      if (column.default) {
        convertedColumn.default = true;
        convertedColumn.selected = true;
      }
      if (column["filter type"] !== FILTER_TYPE_NONE) {
        convertedColumn.type = column["filter type"];
      }
      accumColumns.push(convertedColumn);
    }
    return accumColumns;
  }, []);
}