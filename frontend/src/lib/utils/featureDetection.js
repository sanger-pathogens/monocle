export function localStorageAvailable() {
  try {
    const x = "__storage_test";
    localStorage.setItem(x, x);
    localStorage.removeItem(x);
    return true;
  }
  catch(e) {
    return false;
  }
}
