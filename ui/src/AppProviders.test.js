import React from "react";
import { renderHook } from "@testing-library/react-hooks";

import AppProviders from "./AppProviders";
import { useAuth } from "./auth";
import { useUser } from "./user";
import { useDownloading } from "./downloading";

describe("AppProviders", () => {
  // helper
  const wrapper = ({ children }) => <AppProviders>{children}</AppProviders>;

  it("should provide AuthContext", () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper,
    });

    expect(result.current).toHaveProperty("isLoggedIn");
    expect(result.current).toHaveProperty("isLoading");
    expect(result.current).toHaveProperty("login");
    expect(result.current).toHaveProperty("logout");
  });

  it("should provide UserContext", () => {
    const { result } = renderHook(() => useUser(), {
      wrapper,
    });

    expect(result.current).toHaveProperty("user");
  });

  it("should provide DownloadingContext", () => {
    const { result } = renderHook(() => useDownloading(), {
      wrapper,
    });

    expect(result.current).toHaveProperty("isDownloading");
    expect(result.current).toHaveProperty("downloadSample");
  });
});
