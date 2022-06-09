class ResizeObserver {
  observe() {}
  unobserve() {}
}
global.ResizeObserver = ResizeObserver;

global.fetch = () => {};

global.structuredClone = (original) => JSON.parse(JSON.stringify(original));
