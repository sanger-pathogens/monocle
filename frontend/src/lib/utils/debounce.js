const MAX_CALLBACK_FREQUENCY_MS = 800;

// Rate limit a passed function. If a falsy `timeoutId` is passed, call the function w/o delay and return `true`
// as a `timeoutId`.
export default function debounce(
  callback,
  timeoutId,
  maxCallbackFrequencyMs = MAX_CALLBACK_FREQUENCY_MS
) {
  if (!timeoutId) {
    callback();
    return true;
  }
  // Clear the previous timeout and set and return a new one.
  clearTimeout(timeoutId);
  return setTimeout(callback, maxCallbackFrequencyMs);
}
