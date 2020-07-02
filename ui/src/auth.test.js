import React from "react";
import { renderHook, act } from "@testing-library/react-hooks";

import { RealAuthProvider, AlwaysLoggedInAuthProvider, useAuth } from "./auth";
import { mockUser, generateApiMocks } from "./test-utils/apiMocks";
import { MockApolloProvider } from "./test-utils/MockProviders";

describe("AlwaysLoggedInAuthProvider", () => {
  // helper
  const wrapper = ({ children }) => (
    <AlwaysLoggedInAuthProvider>{children}</AlwaysLoggedInAuthProvider>
  );

  it("should be logged in initially", () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper,
    });

    expect(result.current.isLoggedIn).toBe(true);
  });

  it("should still be logged in after calling login", () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.login();
    });

    expect(result.current.isLoggedIn).toBe(true);
  });

  it("should still be logged in after calling logout", () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.logout();
    });

    expect(result.current.isLoggedIn).toBe(true);
  });
});

describe("RealAuthProvider", () => {
  // helper
  const wrapper = ({ apiMocks, children }) => (
    <MockApolloProvider apiMocks={apiMocks}>
      <RealAuthProvider>{children}</RealAuthProvider>
    </MockApolloProvider>
  );

  it("should not be logged in initially", async () => {
    const { mocks: apiMocks } = generateApiMocks();
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await waitForNextUpdate();

    expect(result.current.isLoggedIn).toBe(false);
  });

  it("should be logged in after calling login", async () => {
    const { called, mocks: apiMocks } = generateApiMocks();
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      result.current.login({
        email: mockUser.email,
        password: mockUser.email.split("@")[0],
      });
      await waitForNextUpdate();
    });

    // query made?
    expect(called.loginMutation).toBeGreaterThan(0);

    // authenticated?
    expect(result.current.isLoggedIn).toBe(true);
  });

  it("should be logged out after calling login then logout", async () => {
    const { called, mocks: apiMocks } = generateApiMocks();
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      result.current.login({
        email: mockUser.email,
        password: mockUser.email.split("@")[0],
      });
      result.current.logout();
      await waitForNextUpdate();
    });

    // query made?
    expect(called.logoutMutation).toBeGreaterThan(0);

    // authenticated?
    expect(result.current.isLoggedIn).toBe(false);
  });
});
