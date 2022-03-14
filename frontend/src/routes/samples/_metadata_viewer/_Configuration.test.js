import { fireEvent, render } from "@testing-library/svelte";
import { get } from "svelte/store";
import { DATA_TYPES, LOCAL_STORAGE_KEY_COLUMNS_STATE } from "$lib/constants.js";
import { columnsStore } from "../_stores.js";
import Configuration from "./_Configuration.svelte";

const LABEL_APPLY_AND_CLOSE = "Apply and close";
const LABEL_CLOSE = "Close";
const LABEL_DIALOG = "Select displayed columns";
const LABEL_RESTORE = "Restore default columns";
const LABEL_SETTINGS = /^Select columns/;
const ROLE_BUTTON = "button";

beforeEach(() => {
  columnsStore.set({
    metadata: [{
      name: "Category A", columns: [{
        name: "a", displayName: "A", selected: true
      }, {
        name: "country", displayName: "Country"
      }]
    }],
    "in silico": [{
      name: "Category B", columns: [{
        name: "c", displayName: "C", selected: true
      }, {
        name: "d", displayName: "D"
      }]
    }]
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
  const columnsState = {
    metadata: [{
      name: "Category A", columns: [{
        name: "a", displayName: "A", selected: true
      }, {
        name: "country", displayName: "Country"
      }]
    }],
    "in silico": [{
      name: "Category B", columns: [{
        name: "c", displayName: "C", selected: true
      }, {
        name: "d", displayName: "D"
      }]
    }]
  };
  const { getByLabelText, getByRole } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

  DATA_TYPES.forEach((dataType) =>
    columnsState[dataType].forEach((category) => {
      expect(getByLabelText(new RegExp(`${category.name} `))).toBeDefined();
      category.columns.forEach((column) =>
        expect(getByLabelText(column.displayName)).toBeDefined());
    }));
});

it("saves a columns state to the local storage on apply", async () => {
  const { getByRole } = render(Configuration);
  Storage.prototype.setItem = jest.fn();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_APPLY_AND_CLOSE }));

  // 2 times because it's first called by the feature detection.
  expect(localStorage.setItem).toHaveBeenCalledTimes(2);
  expect(localStorage.setItem).toHaveBeenCalledWith(
    LOCAL_STORAGE_KEY_COLUMNS_STATE, JSON.stringify(get(columnsStore)));
});

it("saves a columns state to the local storage on restore", async () => {
  const { getByRole } = render(Configuration);
  Storage.prototype.setItem = jest.fn();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESTORE }));

  // 2 times because it's first called by the feature detection.
  expect(localStorage.setItem).toHaveBeenCalledTimes(2);
  expect(localStorage.setItem).toHaveBeenCalledWith(
    LOCAL_STORAGE_KEY_COLUMNS_STATE, JSON.stringify(get(columnsStore)));
});

it("saves a columns state to the local storage on restore", async () => {
  columnsStore.setToDefault = jest.fn();
  const { getByRole } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_RESTORE }));

  expect(columnsStore.setToDefault).toHaveBeenCalledTimes(1);
});

it("closes on apply", async () => {
  const { getByRole, queryByLabelText } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_APPLY_AND_CLOSE }));

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

it("closes on Close click", async () => {
  const { getByRole, queryByLabelText } = render(Configuration);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CLOSE }));

  expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
});

describe("on empty columns state", () => {
  beforeEach(() => columnsStore.set(undefined));

  it("displays an error message", async () => {
    const { getByRole, getByText } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));

    expect(getByText(/^Something went wrong. Please try to reload the page/)).toBeDefined();
  });

  it("closes on Close click", async () => {
    const { getByRole, queryByLabelText } = render(Configuration);

    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_SETTINGS }));
    await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_CLOSE }));

    expect(queryByLabelText(LABEL_DIALOG)).toBeNull();
  });
});
