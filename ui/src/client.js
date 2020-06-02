import { ApolloClient } from "apollo-client";
import { InMemoryCache } from "apollo-cache-inmemory";
import { from } from "apollo-link";
import { HttpLink } from "apollo-link-http";
import { onError } from "apollo-link-error";

import history from "./history";

const appCache = new InMemoryCache();

const httpLink = new HttpLink({
  uri: window.env.GRAPHQL_API_URL,
  credentials: "include",
});
const errorLink = onError(({ graphQLErrors, networkError }) => {
  // TODO: handle network errors globally?
  if (graphQLErrors) {
    graphQLErrors.map(({ message, locations, path }) => {
      if (message === "Signature has expired") {
        // access token has expired...
        // TODO: attempt to get a new access token (once only)

        // update state
        localStorage.removeItem("isLoggedIn");

        // request credentials
        history.push("/login");
      } else if (message === "Refresh token is expired") {
        // refresh token has expired...

        // update state
        localStorage.removeItem("isLoggedIn");

        // request credentials
        history.push("/login");
      } else if (
        message === "You do not have permission to perform this action"
      ) {
        // attempted to access a private query,
        // (shouldn't happen, unless user manually
        // visits eg. /me whilst logged out)

        // update state
        localStorage.removeItem("isLoggedIn");

        // request credentials
        history.push("/login");
      }
    });
  }
});

const client = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: appCache,
});

export default client;
