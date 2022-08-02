import { sessionStorageAvailable } from "$lib/utils/featureDetection.js";

it("returns `true` if `sessionStorage` is available", () => {
  expect(sessionStorageAvailable()).toBeTruthy();
});

it("returns `false` if `sessionStorage` isn't available", () => {
  Storage.prototype.setItem = jest.fn(() => {
    throw "some error";
  });

  expect(sessionStorageAvailable()).toBeFalsy();
});
