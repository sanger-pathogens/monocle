const MAX_CALLBACK_FREQUENCY_MS = 1200;

export default function debounce(callback, timeoutId, maxCallbackFrequencyMs = MAX_CALLBACK_FREQUENCY_MS) {
  // Clear the previous timeout and set and return a new one.
  clearTimeout(timeoutId);
  return setTimeout(callback, maxCallbackFrequencyMs);
}
