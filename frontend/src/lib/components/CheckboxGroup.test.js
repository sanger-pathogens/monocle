import { fireEvent, render } from "@testing-library/svelte";
import CheckboxGroup from "./CheckboxGroup.svelte";

const ITEM_NAMES = ["Kiev", "Tbilisi"];
const NAME_GROUP = "Cities";
const RE_NAME_GROUP = new RegExp(` ${NAME_GROUP} `);

it("isn't rendered if no items are passed", () => {
  const { container } = render(CheckboxGroup, { groupName: NAME_GROUP });

  expect(container.innerHTML).toBe("<div></div>");
});

it("is closed by default if no items are checked", () => {
  const { queryByLabelText, getByLabelText } = render(CheckboxGroup, {
    groupName: NAME_GROUP,
    items: [{ displayName: ITEM_NAMES[0] }] });

  expect(queryByLabelText(ITEM_NAMES[0])).toBeNull();
  expect(getByLabelText(RE_NAME_GROUP).indeterminate).toBeFalsy();
});

it("is open by default if all items are checked", () => {
  const { queryByLabelText, getByLabelText } = render(CheckboxGroup, {
    groupName: NAME_GROUP,
    items: [{ displayName: ITEM_NAMES[0], checked: true }] });

  expect(queryByLabelText(ITEM_NAMES[0])).toBeNull();
  expect(getByLabelText(RE_NAME_GROUP).indeterminate).toBeFalsy();
});

it("is open by default if only some items are checked", () => {
  const { getByLabelText } = render(CheckboxGroup, {
    groupName: NAME_GROUP,
    items: [{ displayName: ITEM_NAMES[0] }, { displayName: ITEM_NAMES[1], checked: true }] });

  expect(getByLabelText(ITEM_NAMES[0])).toBeDefined();
  expect(getByLabelText(RE_NAME_GROUP).indeterminate).toBeTruthy();
});

it("can be expanded and collapsed", async () => {
  const { container, getByLabelText, queryByLabelText } = render(CheckboxGroup, {
    groupName: NAME_GROUP,
    items: [{ displayName: ITEM_NAMES[0] }, { displayName: ITEM_NAMES[1] }] });
  const groupLabel = container.getElementsByClassName("expand-icon")[0];

  expect(queryByLabelText(ITEM_NAMES[0])).toBeNull();

  await fireEvent.click(groupLabel);

  expect(getByLabelText(ITEM_NAMES[0])).toBeDefined();

  await fireEvent.click(groupLabel);

  expect(queryByLabelText(ITEM_NAMES[0])).toBeNull();
});

it("shows the right number of selected items", async () => {
  const items = [{ displayName: ITEM_NAMES[0], checked: true }, { displayName: ITEM_NAMES[1] }];
  const numItems = items.length;
  const { getByLabelText } = render(CheckboxGroup, { groupName: NAME_GROUP, items });

  expect(getByLabelText(new RegExp(`1/${numItems}`))).toBeDefined();

  await fireEvent.click(getByLabelText(ITEM_NAMES[0]));

  expect(getByLabelText(new RegExp(`0/${numItems}`))).toBeDefined();

  await fireEvent.click(getByLabelText(RE_NAME_GROUP));

  expect(getByLabelText(new RegExp(`${numItems}/${numItems}`))).toBeDefined();

  await fireEvent.click(getByLabelText(RE_NAME_GROUP));

  expect(getByLabelText(new RegExp(`0/${numItems}`))).toBeDefined();
});
