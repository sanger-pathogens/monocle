import { loadUserRole } from "./_dataLoading.js";

describe("loading user role", () => {
  const USER_ROLE = "support";

  const fetch = jest.fn(() => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(
      { user_details: { type: USER_ROLE } })
  }));

  it("fetches the role from the correct endpoint", () => {
    loadUserRole(fetch);

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith("/dashboard-api/get_user_details");
  });

  it("returns the user role from the response", async () => {
    const userRole = await loadUserRole(fetch);

    expect(userRole).toBe(USER_ROLE);
  });

  describe("returns `undefined`", () => {
    it("when the type field from user details is missing", async () => {
      fetch.mockImplementation(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(
          { user_details: {} })
      }));

      const userRole = await loadUserRole(fetch);

      expect(userRole).toBeUndefined();
    });

    it("when user details are missing", async () => {
      fetch.mockImplementation(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      }));

      const userRole = await loadUserRole(fetch);

      expect(userRole).toBeUndefined();
    });

    it("when the fetch request rejects", async () => {
      fetch.mockImplementation(() => Promise.resolve({
        ok: true,
        json: () => Promise.reject()
      }));

      const userRole = await loadUserRole(fetch);

      expect(userRole).toBeUndefined();
    });

    it("when the fetch request rejects", async () => {
      fetch.mockImplementation(() => Promise.resolve({
        ok: false
      }));

      const userRole = await loadUserRole(fetch);

      expect(userRole).toBeUndefined();
    });
  });
});
