import debounce from "./debounce.js";

const DEFAULT_MAX_CALLBACK_FREQUENCY_MS = 800;

it(`calls a passed function immediately if a falsy timeout ID is passed and prevents the function from
 being called more often than the default frequency`, () => {
  const someFunction = jest.fn();
  jest.useFakeTimers();
  jest.spyOn(global, "clearTimeout");
  jest.spyOn(global, "setTimeout");

  let timeoutId = debounce(someFunction);
  timeoutId = debounce(someFunction, timeoutId);
  debounce(someFunction, timeoutId);

  expect(someFunction).toHaveBeenCalledTimes(1);

  jest.runAllTimers();

  expect(someFunction).toHaveBeenCalledTimes(2);
  const clearTimeoutCallOrder = clearTimeout.mock.invocationCallOrder[0];
  const setTimeoutCallOrder = setTimeout.mock.invocationCallOrder[0];
  expect(clearTimeoutCallOrder).toBeLessThan(setTimeoutCallOrder);
  const numTimesCallbackDelayed = 2;
  expect(setTimeout).toHaveBeenCalledTimes(numTimesCallbackDelayed);
  setTimeout.mock.calls.forEach((args) => {
    expect(args).toEqual([someFunction, DEFAULT_MAX_CALLBACK_FREQUENCY_MS]);
  });
  expect(clearTimeout).toHaveBeenCalledTimes(numTimesCallbackDelayed);
  expect(clearTimeout).toHaveBeenCalledWith(timeoutId);
});

it("accepts optional max frequency", () => {
  const someFunction = () => {};
  const maxCallbackFrequencyMs = DEFAULT_MAX_CALLBACK_FREQUENCY_MS + 100;
  jest.spyOn(global, "setTimeout");

  const timeoutId = debounce(someFunction, undefined, maxCallbackFrequencyMs);
  debounce(someFunction, timeoutId, maxCallbackFrequencyMs);

  expect(setTimeout).toHaveBeenCalledWith(someFunction, maxCallbackFrequencyMs);
});
