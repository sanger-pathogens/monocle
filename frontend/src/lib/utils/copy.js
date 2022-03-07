export const deepCopy = window.structuredClone || ((original) => JSON.parse( JSON.stringify(original) ));
