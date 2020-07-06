import React from "react";
import { renderHook, act } from "@testing-library/react-hooks";

import { RealAuthProvider, AlwaysLoggedInAuthProvider, useAuth } from "./auth";
import {
  ERROR_BAD_CREDENTIALS,
  ERROR_NO_AUTH_TOKEN,
  ERROR_NO_REFRESH_TOKEN,
} from "./client";
import {
  mockUser,
  generateApiMocks,
  mockDefaults,
} from "./test-utils/apiMocks";
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

  it("should not be logged in initially if no tokens", async () => {
    const mocks = {
      ...mockDefaults,
      verify: null,
      verifyErrors: [ERROR_NO_AUTH_TOKEN],
      refresh: null,
      refreshErrors: [ERROR_NO_REFRESH_TOKEN],
    };
    const { called, mocks: apiMocks } = generateApiMocks(mocks);
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      // verify
      await waitForNextUpdate();

      // refresh
      await waitForNextUpdate();
    });

    expect(result.current.isLoggedIn).toBe(false);
  });

  it("should be logged in initially if auth token", async () => {
    const { mocks: apiMocks } = generateApiMocks();
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      // verify
      await waitForNextUpdate();
    });

    expect(result.current.isLoggedIn).toBe(true);
  });

  it("should be logged in initially if no auth token but refresh token", async () => {
    const mocks = {
      ...mockDefaults,
      verify: null,
      verifyErrors: [ERROR_NO_AUTH_TOKEN],
    };
    const { called, mocks: apiMocks } = generateApiMocks(mocks);
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      // verify
      await waitForNextUpdate();

      // refresh
      await waitForNextUpdate();
    });

    expect(result.current.isLoggedIn).toBe(true);
  });

  it("should be logged in after calling login", async () => {
    const mocks = {
      ...mockDefaults,
      verify: null,
      verifyErrors: [ERROR_NO_AUTH_TOKEN],
      refresh: null,
      refreshErrors: [ERROR_NO_REFRESH_TOKEN],
    };
    const { called, mocks: apiMocks } = generateApiMocks(mocks);
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      // verify
      await waitForNextUpdate();

      // refresh
      await waitForNextUpdate();

      // login
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

  it("should not be logged in after calling login unsuccessfully", async () => {
    const mocks = {
      ...mockDefaults,
      verify: null,
      verifyErrors: [ERROR_NO_AUTH_TOKEN],
      refresh: null,
      refreshErrors: [ERROR_NO_REFRESH_TOKEN],
      login: null,
      loginErrors: [ERROR_BAD_CREDENTIALS],
    };
    const { called, mocks: apiMocks } = generateApiMocks(mocks);
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      // verify
      await waitForNextUpdate();

      // refresh
      await waitForNextUpdate();

      // login
      result.current.login({
        email: mockUser.email,
        password: mockUser.email.split("@")[0],
      });
      await waitForNextUpdate();
    });

    // query made?
    expect(called.loginMutation).toBeGreaterThan(0);

    // authenticated?
    expect(result.current.isLoggedIn).toBe(false);
  });

  it("should be logged out after calling login then logout", async () => {
    const mocks = {
      ...mockDefaults,
      verify: null,
      verifyErrors: [ERROR_NO_AUTH_TOKEN],
      refresh: null,
      refreshErrors: [ERROR_NO_REFRESH_TOKEN],
    };
    const { called, mocks: apiMocks } = generateApiMocks(mocks);
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper,
      initialProps: { apiMocks },
    });

    await act(async () => {
      // verify
      await waitForNextUpdate();

      // refresh
      await waitForNextUpdate();

      // login
      result.current.login({
        email: mockUser.email,
        password: mockUser.email.split("@")[0],
      });
      await waitForNextUpdate();

      // logout
      result.current.logout();
      await waitForNextUpdate();
    });

    // query made?
    expect(called.logoutMutation).toBeGreaterThan(0);

    // authenticated?
    expect(result.current.isLoggedIn).toBe(false);
  });
});
