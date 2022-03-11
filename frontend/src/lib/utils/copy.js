export const deepCopy = (original) => {
  try {
    return structuredClone(original);
  } catch (err) {
    console.warn(
      `Error on trying to copy \`${original}\` w/ \`structuredClone()\`: ${err}. Falling back to JSON's stringify-parse.`);
    return JSON.parse( JSON.stringify(original) );
  }
};
