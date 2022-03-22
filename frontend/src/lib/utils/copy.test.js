const ORIGINAL = { k: { things: [{ k: 42 }, { k: null }] } };

afterEach(() => {
  jest.resetModules();
});

it("delegates to `structuredClone`", async () => {
  global.structuredClone = jest.fn();
  const { deepCopy } = await import("./copy.js");

  deepCopy(ORIGINAL);

  expect(structuredClone).toHaveBeenCalledTimes(1);
  expect(structuredClone).toHaveBeenCalledWith(ORIGINAL);
});

it("works even if `structuredClone` isn't supported", async () => {
  global.structuredClone = undefined;
  global.console.warn = () => {};
  const { deepCopy } = await import("./copy.js");

  const copy = deepCopy(ORIGINAL);

  expect(copy).toStrictEqual(ORIGINAL);
  expect(copy).not.toBe(ORIGINAL);
});
