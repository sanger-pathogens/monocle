import React from "react";
import { renderHook, act } from "@testing-library/react-hooks";

import { AlwaysLoggedInAuthProvider, useAuth } from "./auth";

describe("AlwaysLoggedInAuthProvider", () => {
  // helper
  const wrapper = ({ children }) => (
    <AlwaysLoggedInAuthProvider>{children}</AlwaysLoggedInAuthProvider>
  );

  it("should be logged in initially", () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

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
