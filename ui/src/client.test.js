import { graphql } from "msw";

import { server } from "./test-utils/server";
import {
  ERROR_NO_AUTH_TOKEN,
  ERROR_NO_REFRESH_TOKEN,
  handleBadPermissions,
} from "./client";

import authFetchers from "./authFetchers";
import history from "./history";

describe("handleBadPermissions", () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test("works when both tokens are expired", async () => {
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
