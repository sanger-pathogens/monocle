import React from "react";
import { ApolloProvider } from "@apollo/react-hooks";
import { graphql } from "msw";
import { renderHook } from "@testing-library/react-hooks";

import { server } from "./test-utils/server";
import client, {
  ERROR_NO_AUTH_TOKEN,
  ERROR_NO_REFRESH_TOKEN,
  ERROR_BAD_PERMISSIONS,
  handleBadPermissions,
} from "./client";

import authFetchers from "./authFetchers";
import history from "./history";
import { useUser } from "./user";
import { RealAuthProvider } from "./auth";
import { RealUserProvider } from "./user";
import { mockUser, mockVerifyTokenSuccess } from "./test-utils/apiMocks";

describe("handleBadPermissions", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("works when both tokens are expired", async () => {
    // specify api responses
    server.use(
      graphql.mutation("VerifyToken", (_, res, ctx) =>
        res(ctx.errors([{ message: ERROR_NO_AUTH_TOKEN }]))
      ),
      graphql.mutation("RefreshToken", (_, res, ctx) =>
        res(ctx.errors([{ message: ERROR_NO_REFRESH_TOKEN }]))
      )
    );

    // set up spies
    jest.spyOn(authFetchers, "verifyToken");
    jest.spyOn(authFetchers, "refreshToken");
    jest.spyOn(history, "push");

    // act
    await handleBadPermissions();

    // assert
    expect(authFetchers.verifyToken).toHaveBeenCalled();
    expect(authFetchers.refreshToken).toHaveBeenCalled();
    expect(history.push).toHaveBeenCalledWith("/");
  });
});

describe("errorLink", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  // helper
  const wrapper = ({ children }) => (
    <ApolloProvider client={client}>
      <RealAuthProvider>
        <RealUserProvider>{children}</RealUserProvider>
      </RealAuthProvider>
    </ApolloProvider>
  );

  it("successfully retries private query on successful auth token verification", async () => {
    // specify initial api responses
    server.use(
      graphql.query("User", (_, res, ctx) =>
        res(ctx.errors([{ message: ERROR_BAD_PERMISSIONS }]))
      ),
      graphql.mutation("VerifyToken", (_, res, ctx) =>
        res(ctx.data({ verifyToken: mockVerifyTokenSuccess }))
      )
    );

    // set up spies
    jest.spyOn(authFetchers, "verifyToken");
    jest.spyOn(authFetchers, "refreshToken");
    jest.spyOn(history, "push");

    // get context
    const { result, waitForNextUpdate } = renderHook(() => useUser(), {
      wrapper,
    });

    // act
    result.current.getUser();
    await waitForNextUpdate();

    // assert
    expect(result.current.user).toBeNull();
    expect(authFetchers.verifyToken).toHaveBeenCalledTimes(1);

    // specify new api response for retry
    server.use(
      graphql.query("User", (_, res, ctx) => res(ctx.data({ me: mockUser })))
    );
    await waitForNextUpdate();

    // assert
    expect(result.current.user).not.toBeNull();
    expect(authFetchers.verifyToken).toHaveBeenCalledTimes(1);
    expect(authFetchers.refreshToken).not.toHaveBeenCalled();
  });
});
