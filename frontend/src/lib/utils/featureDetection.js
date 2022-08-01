export function sessionStorageAvailable() {
  try {
    const x = "__storage_test";
    sessionStorage.setItem(x, x);
    sessionStorage.removeItem(x);
    return true;
  } catch (e) {
    return false;
  }
}
