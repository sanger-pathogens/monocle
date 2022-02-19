import { localStorageAvailable } from "$lib/utils/featureDetection.js";

it("returns `true` if `localStorage` is available", () => {
  expect(localStorageAvailable()).toBeTruthy();
});

it("returns `false` if `localStorage` isn't available", () => {
  Storage.prototype.setItem = jest.fn(() => {throw "some error"});

  expect(localStorageAvailable()).toBeFalsy();
});
