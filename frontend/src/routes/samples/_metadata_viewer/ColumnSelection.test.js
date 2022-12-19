import { render } from "@testing-library/svelte";
import ColumnSelection from "./ColumnSelection.svelte";

const COLUMNS_DATA = [
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
  {
    name: "Category B",
    columns: [
      {
        name: "columnX",
        displayName: "Column X",
        selected: true,
      },
      {
        name: "st",
        displayName: "ST",
      },
    ],
  },
];
const EMPTY_HTML = "<div></div>";

it("correctly displays column data", () => {
  const { getByLabelText } = render(ColumnSelection, {
    columnsData: COLUMNS_DATA,
  });

  COLUMNS_DATA.forEach((category) => {
    expect(getByLabelText(new RegExp(`${category.name} `))).toBeDefined();
    category.columns.forEach((column) =>
      expect(getByLabelText(column.displayName)).toBeDefined()
    );
  });
});

it("isn't shown w/o columns data", () => {
  const { container } = render(ColumnSelection);

  expect(container.innerHTML).toBe(EMPTY_HTML);
});

it("isn't shown w/ empty columns data", () => {
  const { container } = render(ColumnSelection, { columnsData: [] });

  expect(container.innerHTML).toBe(EMPTY_HTML);
});

it("can be collapsed", async () => {
  const ROLE_GROUP = "group";
  const { component, getByRole } = render(ColumnSelection, {
    columnsData: COLUMNS_DATA,
  });

  expect(getByRole(ROLE_GROUP).open).toBeTruthy();

  await component.$set({ open: false });

  expect(getByRole(ROLE_GROUP).open).toBeFalsy();
});
