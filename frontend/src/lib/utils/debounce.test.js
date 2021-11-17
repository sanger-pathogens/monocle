import debounce from "./debounce.js";

const DEFAULT_MAX_CALLBACK_FREQUENCY_MS = 1200;

it("prevents a passed function from being called more often than the default frequency", () => {
  const someFunction = jest.fn();
  jest.useFakeTimers();
  jest.spyOn(global, "clearTimeout");
  jest.spyOn(global, "setTimeout");

  let timeoutId = debounce(someFunction);
  timeoutId = debounce(someFunction, timeoutId);
  debounce(someFunction, timeoutId);

  expect(someFunction).not.toHaveBeenCalled();

  jest.runAllTimers();

  expect(someFunction).toHaveBeenCalledTimes(1);
  let clearTimeoutCallOrder = clearTimeout.mock.invocationCallOrder[0];
  let setTimeoutCallOrder = setTimeout.mock.invocationCallOrder[0];
  expect(clearTimeoutCallOrder).toBeLessThan(setTimeoutCallOrder);
  const numTimesDebounceCalled = 3;
  expect(setTimeout).toHaveBeenCalledTimes(numTimesDebounceCalled);
  setTimeout.mock.calls.forEach((args) => {
    expect(args).toEqual([someFunction, DEFAULT_MAX_CALLBACK_FREQUENCY_MS]);
  });
  expect(clearTimeout).toHaveBeenCalledTimes(numTimesDebounceCalled);
  expect(clearTimeout).toHaveBeenCalledWith(timeoutId);
});

it("accepts optional max frequency", () => {
  const someFunction = () => {};
  const maxCallbackFrequencyMs = DEFAULT_MAX_CALLBACK_FREQUENCY_MS + 100;
  jest.spyOn(global, "setTimeout");

  debounce(someFunction, undefined, maxCallbackFrequencyMs);

  expect(setTimeout).toHaveBeenCalledWith(someFunction, maxCallbackFrequencyMs);
});
