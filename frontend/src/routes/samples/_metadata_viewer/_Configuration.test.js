import { fireEvent, render } from "@testing-library/svelte";
import { get } from "svelte/store";
import { DATA_TYPES, LOCAL_STORAGE_KEY_COLUMNS_STATE } from "$lib/constants.js";
import { columnsStore, filterStore } from "../_stores.js";
import Configuration from "./_Configuration.svelte";

const KEY_DISABLED = "disabled";
const KEY_SELECTED = "selected";
const LABEL_APPLY_AND_CLOSE = "Apply and close";
const LABEL_CLOSE = "Close";
const LABEL_DIALOG = "Select displayed columns";
const LABEL_RESTORE = "Restore default columns";
const LABEL_SETTINGS = /^Select columns/;
const ROLE_BUTTON = "button";

beforeEach(() => {
  columnsStore.set({
    metadata: [
      {
        name: "Category A",
        columns: [
          {
            name: "columnA",
            displayName: "Column A",
            selected: true,
          },
          {
            name: "country",
            displayName: "Country",
          },
        ],
      },
    ],
    "in silico": [
      {
        name: "Category B",
        columns: [
          {
            name: "columnC",
            displayName: "Column C",
            selected: true,
          },
          {
            name: "columnD",
            displayName: "Column D",
          },
        ],
      },
    ],
  });
});

it("opens on settings button click", async () => {
  const { getByLabelText, getByRole, queryByLabelText } = render(Configuration);

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

  expect(getByLabelText(LABEL_DIALOG)).toBeDefined();
});

it("metadata and in silico section are open by default", async () => {
  const { container, getByRole } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

  const dataTypeSections = container.getElementsByTagName("details");
  expect(dataTypeSections.length).toBe(2);
  for (const dataTypeSection of dataTypeSections) {
    expect(dataTypeSection.open).toBeTruthy();
  }
});

it("correctly displays a column state", async () => {
  const { getByLabelText, getByRole } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

  const columnsState = get(columnsStore);
  DATA_TYPES.forEach((dataType) =>
    columnsState[dataType].forEach((category) => {
      expect(getByLabelText(new RegExp(`${category.name} `))).toBeDefined();
      category.columns.forEach((column) =>
        expect(getByLabelText(column.displayName)).toBeDefined()
      );
    })
  );
});

it("saves a columns state to the local storage on apply", async () => {
  const { getByRole } = render(Configuration);
  Storage.prototype.setItem = jest.fn();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(
    getByRole(ROLE_BUTTON, { name: LABEL_APPLY_AND_CLOSE })
  );

  // 2 times because it's first called by the feature detection.
  expect(localStorage.setItem).toHaveBeenCalledTimes(2);
  expect(localStorage.setItem).toHaveBeenCalledWith(
    LOCAL_STORAGE_KEY_COLUMNS_STATE,
    JSON.stringify(get(columnsStore), cleanupColumnsStateReplacer)
  );
});

it("saves a columns state to the local storage on restore", async () => {
  const { getByRole } = render(Configuration);
  Storage.prototype.setItem = jest.fn();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESTORE }));

  // 2 times because it's first called by the feature detection.
  expect(localStorage.setItem).toHaveBeenCalledTimes(2);
  expect(localStorage.setItem).toHaveBeenCalledWith(
    LOCAL_STORAGE_KEY_COLUMNS_STATE,
    JSON.stringify(get(columnsStore), cleanupColumnsStateReplacer)
  );
});

it("sets the column state to default on restore", async () => {
  columnsStore.setToDefault = jest.fn();
  const { getByRole } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESTORE }));

  expect(columnsStore.setToDefault).toHaveBeenCalledTimes(1);
});

it("closes on apply", async () => {
  const { getByRole, queryByLabelText } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(
    getByRole(ROLE_BUTTON, { name: LABEL_APPLY_AND_CLOSE })
  );

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

it("closes on Close click", async () => {
  const { getByRole, queryByLabelText } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CLOSE }));

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

describe("on filter", () => {
  const COLUMNS_WTH_ACTIVE_FILTERS = [
    {
      name: "columnA",
      displayName: "Column A",
    },
    {
      name: "columnC",
      displayName: "Column C",
    },
  ];
  const SOME_VALUE = "val";

  beforeEach(() => {
    filterStore.update((filterState) => {
      filterState.metadata[COLUMNS_WTH_ACTIVE_FILTERS[0].name] = {
        values: [SOME_VALUE],
      };
      filterState["in silico"][COLUMNS_WTH_ACTIVE_FILTERS[1].name] = {
        values: [SOME_VALUE],
      };
      return filterState;
    });
  });

  it("disables corresponding columns", async () => {
    const { container, getByRole, getByLabelText } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

    expect(container.querySelectorAll("input[disabled]").length).toBe(
      COLUMNS_WTH_ACTIVE_FILTERS.length
    );
    COLUMNS_WTH_ACTIVE_FILTERS.forEach((column) =>
      expect(
        getByLabelText(new RegExp(`^${column.displayName}\\*`)).disabled
      ).toBeTruthy()
    );
  });

  it("shows the explanation message and has the correct tooltip for each disabled item", async () => {
    const expectedTooltipText =
      "* To de-select this column, first remove the column's filter.";
    const { getByLabelText, getByRole, getByText } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

    expect(
      getByText(
        "* To de-select a column with an active filter, first remove the filter."
      )
    ).toBeDefined();
    COLUMNS_WTH_ACTIVE_FILTERS.forEach((column) => {
      const actualTooltipText = getByLabelText(
        new RegExp(`^${column.displayName}\\*`)
      ).parentNode.parentNode.title;
      expect(actualTooltipText).toBe(expectedTooltipText);
    });
  });

  it("removes active filters and enables all column checkboxes on restore", async () => {
    global.confirm = jest.fn(() => true);
    const { container, getByRole } = render(Configuration);
    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESTORE }));

    expect(confirm).toHaveBeenCalledTimes(1);
    expect(confirm).toHaveBeenCalledWith(
      "Restoring default columns will remove all filters. Proceed?"
    );
    expect(container.querySelectorAll("input[disabled]").length).toBe(0);
  });

  it("ignores `disabled` in a state if there are no filters", async () => {
    filterStore.removeAllFilters();
    const columns = COLUMNS_WTH_ACTIVE_FILTERS.slice(0, 3);
    columnsStore.set({
      metadata: [
        {
          name: "Category A",
          columns: [
            {
              name: columns[0].name,
              displayName: columns[0].displayName,
              selected: true,
              disabled: true,
            },
            {
              name: columns[1].name,
              displayName: columns[1].displayName,
            },
          ],
        },
      ],
    });
    const { container, getByLabelText, getByRole } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

    expect(container.querySelectorAll("input[disabled]").length).toBe(0);
    columns.forEach((column) =>
      expect(getByLabelText(column.displayName)).toBeDefined()
    );
  });
});

describe("on empty columns state", () => {
  beforeEach(() => columnsStore.set(undefined));

  it("displays an error message", async () => {
    const { getByRole, getByText } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

    expect(
      getByText(/^Something went wrong. Please try to reload the page/)
    ).toBeDefined();
  });

  it("closes on Close click", async () => {
    const { getByRole, queryByLabelText } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CLOSE }));

    expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
  });
});

function cleanupColumnsStateReplacer(key, value) {
  return key === KEY_DISABLED || (key === KEY_SELECTED && !value)
    ? undefined
    : value;
}
