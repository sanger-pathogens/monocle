import React from "react";
import { renderHook } from "@testing-library/react-hooks";

import { RealUserProvider, useUser } from "./user";
import { AuthContext } from "./auth";
import { mockUser, generateApiMocks } from "./test-utils/apiMocks";
import { MockApolloProvider } from "./test-utils/MockProviders";

describe("RealUserProvider", () => {
  // helper
  const wrapper = ({ isLoggedIn, apiMocks, children }) => (
    <MockApolloProvider apiMocks={apiMocks}>
      <AuthContext.Provider value={{ isLoggedIn }}>
        <RealUserProvider>{children}</RealUserProvider>
      </AuthContext.Provider>
    </MockApolloProvider>
  );

  it("should not query if logged out", async () => {
    const { called, mocks: apiMocks } = generateApiMocks();
    renderHook(() => useUser(), {
      wrapper,
      initialProps: { apiMocks, isLoggedIn: false },
    });

    // query made?
    expect(called.userQuery).toEqual(0);
  });

  it("should query and return user if logged in", async () => {
    const { called, mocks: apiMocks } = generateApiMocks();
    const { result, waitForNextUpdate } = renderHook(() => useUser(), {
      wrapper,
      initialProps: { apiMocks, isLoggedIn: true },
    });

    await waitForNextUpdate();

    // query made?
    expect(called.userQuery).toBeGreaterThan(0);

    // user?
    expect(result.current.user.email).toBe(mockUser.email);
  });
});
