import { render } from "@testing-library/svelte";
import Icon from "./_Icon.svelte";

const COLOR = "blue";
const CSS_SELECTOR_ICON = "svg";

it("renders the icon and hides it for screen readers", () => {
  const { container } = render(Icon);

  const icon = container.querySelector(CSS_SELECTOR_ICON);
  expect(icon).toBeDefined();
  expect(icon.getAttribute("aria-hidden")).toBe("true");
});

it("doesn't hide the icon from screen readers if `label` is passed", () => {
  const iconLabel = "please wait";
  const { container, getByText } = render(Icon, { label: iconLabel });

  expect(getByText(iconLabel)).toBeDefined();
  const icon = container.querySelector(CSS_SELECTOR_ICON);
  expect(icon.getAttribute("aria-hidden")).toBeNull();
});

it("can be rendered focusable", async () => {
  const { component, container } = render(Icon);

  const iconElement = container.querySelector(CSS_SELECTOR_ICON);
  expect(iconElement.getAttribute("tabindex")).toBeNull();

  await component.$set({ focusable: true });

  expect(iconElement.getAttribute("tabindex")).toBe("0");
});

it("can be rendered w/ a custom color", () => {
  const { container } = render(Icon, { color: COLOR });

  expect(container.querySelector(CSS_SELECTOR_ICON).getAttribute("fill")).toBe(
    COLOR
  );
});

it("can have a custom CSS class", () => {
  const cssClass = "some-icon";
  const { container } = render(Icon, { cssClass });

  expect(container.querySelector(`.${cssClass}`)).toBeDefined();
});

it("combines inline style as expected", async () => {
  const ATTRIBUTE_NAME_STYLE = "style";
  const customStyle = "  padding: 0   ";

  const { component, container } = render(Icon);

  expect(
    container
      .querySelector(CSS_SELECTOR_ICON)
      .getAttribute(ATTRIBUTE_NAME_STYLE)
  ).toBeNull();

  await component.$set({ style: customStyle });

  expect(
    container
      .querySelector(CSS_SELECTOR_ICON)
      .getAttribute(ATTRIBUTE_NAME_STYLE)
  ).toBe(customStyle.trim());

  await component.$set({ colorHover: COLOR, style: null });

  expect(
    container
      .querySelector(CSS_SELECTOR_ICON)
      .getAttribute(ATTRIBUTE_NAME_STYLE)
  ).toBe(`--color-hover:${COLOR};`);

  await component.$set({ style: customStyle });

  expect(
    container
      .querySelector(CSS_SELECTOR_ICON)
      .getAttribute(ATTRIBUTE_NAME_STYLE)
  ).toBe(`--color-hover:${COLOR};${customStyle}`.trim());
});
