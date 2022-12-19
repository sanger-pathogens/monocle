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
    "qc data": [...],
    "in silico": [...],
  }
```
*/
// IMPORTANT: when changing `columnsStore`, increment `$lib/constants/SESSION_STORAGE_KEY_COLUMNS_STATE`.
function createColumnsStore() {
  const { set, update, subscribe } = writable();

  return {
    set,
    subscribe,
    setFromColumnsResponse: (columnsResponse) =>
      set(convertColumnsResponseToState(columnsResponse)),
    setToDefault: () =>
      update((columnsState) => {
        DATA_TYPES.forEach((dataType) =>
          columnsState[dataType]?.forEach((category) =>
            category.columns.forEach(
              (column) => (column.selected = column.default)
            )
          )
        );
        return columnsState;
      }),
  };
}

export const columnsStore = createColumnsStore();

/*
  `displayedColumnsStore` has the following shape:
  ```
  {
    metadata: [{
      displayName: "Column Name",
      name: "column_name",
      type?: "numeric"
    },
    {...}],
    "qc data": [...],
    "in silico": [...],
  }
  ```
*/
export const displayedColumnsStore = derived(columnsStore, (columnsState) =>
  columnsState
    ? Object.keys(columnsState).reduce((accumDataTypeToColumns, dataType) => {
        accumDataTypeToColumns[dataType] = columnsState[dataType].reduce(
          columnCategoryToColumnsReducer,
          []
        );
        return accumDataTypeToColumns;
      }, {})
    : undefined
);

function columnCategoryToColumnsReducer(accumColumns, category) {
  category.columns.forEach((column) => {
    if (column.selected) {
      accumColumns.push(column);
    }
  });
  return accumColumns;
}

/*
  `displayedColumnNamesStore` has the following shape:
  ```
  {
    metadata: ["column_name_1", "column_name_2"],
    "qc data": [...],
    "in silico": [...],
  }
  ```
*/
export const displayedColumnNamesStore = derived(columnsStore, (columnsState) =>
  columnsState
    ? Object.keys(columnsState).reduce(
        (accumDataTypeToColumnNames, dataType) => {
          accumDataTypeToColumnNames[dataType] = columnsState[dataType].reduce(
            columnCategoryToColumnNamesReducer,
            []
          );
          return accumDataTypeToColumnNames;
        },
        {}
      )
    : undefined
);

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
      "qc data": {...},
      "in silico": {...},
    }
  ```
*/
function createDistinctColumnValuesStore() {
  const { update, set, subscribe } = writable({
    metadata: {},
    "qc data": {},
    "in silico": {},
  });

  return {
    subscribe,
    updateFromDistinctValuesResponse: (distinctValuesResponse) =>
      update((storedDistinctValues) => {
        distinctValuesResponse.forEach(
          ({ "field type": dataType, fields: columns }) =>
            columns.forEach(
              (column) =>
                (storedDistinctValues[dataType][column.name] =
                  column.matches.reduce((accumValues, match) => {
                    if (match.number) {
                      accumValues.push(match.value);
                    }
                    return accumValues;
                  }, []))
            )
        );

        return storedDistinctValues;
      }),
    reset: () => set({ metadata: {}, "qc data": {}, "in silico": {} }),
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
      "qc data": {...},
      "in silico": {...},
    }
  ```
*/
function createFilterStore() {
  const filterCustomStore = writable({
    metadata: {},
    "qc data": {},
    "in silico": {},
  });

  filterCustomStore.removeAllFilters = () =>
    filterCustomStore.set({ metadata: {}, "qc data": {}, "in silico": {} });

  filterCustomStore.removeFilter = (column) =>
    filterCustomStore.update((stotedFilters) => {
      delete stotedFilters[column.dataType][column.name];
      return stotedFilters;
    });

  return filterCustomStore;
}

export const filterStore = createFilterStore();

/*
  `projectStore` has the following shape:
```
  {
    name: "str",
    logoUrl: "str",
    projectUrl: "str",
    headerLinks: [{ label: "str", url: "str" }, ...],
    contacts: [{ label: "str", url: "str" }, ...],
    uploadLinks: [{ label: "str", url: "str" }, ...],
  }
```
*/
function createProjectStore() {
  const { set, subscribe } = writable();
  return {
    setFromResponse: (project = {}) =>
      set({
        name: project.name,
        logoUrl: project.logo_url,
        projectUrl: project.project_url,
        headerLinks: project.header_links,
        contacts: project.contacts,
        uploadLinks: project.upload_links,
      }),
    subscribe,
  };
}

export const projectStore = createProjectStore();

/*
  `userStore` has the following shape:
```
  {
    role: "str",
  }
```
*/
function createUserStore() {
  const { update, subscribe } = writable();
  return {
    setRole: (role) => update((user) => ({ ...(user || {}), role })),
    subscribe,
  };
}

export const userStore = createUserStore();

function convertColumnsResponseToState(columnsResponse) {
  return Object.keys(columnsResponse).reduce((accumColumnsState, dataType) => {
    accumColumnsState[dataType] = transformCategoriesFromResponse(
      columnsResponse[dataType].categories
    );
    return accumColumnsState;
  }, {});
}

function transformCategoriesFromResponse(categories = []) {
  return categories.reduce((accumCategories, category) => {
    const convertedCategory = {
      name: category.name,
      columns: transformColumnsFromResponse(category.fields),
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
        name: column.name,
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
