import { ApolloClient } from "apollo-client";
import { InMemoryCache } from "apollo-cache-inmemory";
import { from } from "apollo-link";
import { HttpLink } from "apollo-link-http";
import { onError } from "apollo-link-error";

import history from "./history";
import env from "./env";
import authFetchers from "./authFetchers";
import promiseToObservable from "./promiseToObservable";

const appCache = new InMemoryCache();

const httpLink = new HttpLink({
  uri: env.GRAPHQL_API_URL,
  credentials: "include",
});

export const ERROR_BAD_CREDENTIALS = "Please enter valid credentials";
export const ERROR_BAD_PERMISSIONS =
  "You do not have permission to perform this action";
export const ERROR_NO_AUTH_TOKEN = "Token is required";
export const ERROR_NO_REFRESH_TOKEN = "Refresh token is required";
export const handleBadPermissions = () =>
  authFetchers
    .verifyToken()
    .then((response) => response.json())
    .then(({ errors }) => {
      if (
        errors &&
        errors.length > 0 &&
        errors[0].message === ERROR_NO_AUTH_TOKEN
      ) {
        return authFetchers
          .refreshToken()
          .then((response) => response.json())
          .then(({ errors }) => {
            if (
              errors &&
              errors.length > 0 &&
              errors[0].message === ERROR_NO_REFRESH_TOKEN
            ) {
              // bomb out and request credentials
              history.push("/");
            }
          });
      }
    })
    .catch((error) => {
      console.error("Failed to handle bad permissions.", error);
    });

const errorLink = onError(({ graphQLErrors, forward, operation }) => {
  if (
    graphQLErrors &&
    graphQLErrors.some(({ message }) => message === ERROR_BAD_PERMISSIONS)
  ) {
    // client getting bad auth likely means that the auth
    // token or refresh token expired, so check with call to
    // verifyToken:
    // - if expired, then refreshToken and retry query
    // - if not expired, then genuine bad auth, allow propagation
    return promiseToObservable(handleBadPermissions()).flatMap(() =>
      forward(operation)
    );
  }
});

const client = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: appCache,
});

export default client;
