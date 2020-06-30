import React, { useState, useEffect } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";

import env from "./env";

const LOGIN_MUTATION = gql`
  mutation Login($email: String!, $password: String!) {
    tokenAuth(email: $email, password: $password) {
      token
    }
  }
`;
const LOGOUT_MUTATION = gql`
  mutation Logout {
    deleteTokenCookie {
      deleted
    }
  }
`;
const REFRESH_MUTATION = gql`
  mutation RefreshToken {
    refreshToken {
      payload
      token
      refreshExpiresIn
    }
  }
`;
const VERIFY_MUTATION = gql`
  mutation VerifyToken {
    verifyToken {
      payload
    }
  }
`;

export const AuthContext = React.createContext();

const RealAuthProvider = (props) => {
  // set initial state (logged out and loading)
  const [state, setState] = useState({
    isLoggedIn: false,
    initialising: true,
  });
  const { isLoggedIn, initialising } = state;

  // graphql mutations for login, logout, verify, refresh
  const [loginMutation, { loading: loggingIn }] = useMutation(LOGIN_MUTATION, {
    onCompleted() {
      // set auth and refresh tokens
      setState({ isLoggedIn: true });
    },
    onError(error) {
      // likely bad credentials
      setState({ isLoggedIn: false });
    },
  });
  const [logoutMutation, { loading: loggingOut }] = useMutation(
    LOGOUT_MUTATION,
    {
      onCompleted() {
        // removing tokens succeeded
        setState({ isLoggedIn: false });
      },
      onError() {
        // removing tokens failed, but can still re-request credentials
        setState({ isLoggedIn: false });
      },
    }
  );
  const [verifyMutation, { loading: verifying }] = useMutation(
    VERIFY_MUTATION,
    {
      onCompleted() {
        // verified that there's a valid auth token
        setState({ isLoggedIn: true });
      },
      onError(error) {
        // no valid auth token, try refreshing
        refreshMutation();
      },
    }
  );
  const [refreshMutation, { loading: refreshing }] = useMutation(
    REFRESH_MUTATION,
    {
      onCompleted() {
        // successfully refreshed auth token
        setState({ isLoggedIn: true });
      },
      onError(error) {
        // no valid refresh token, need credentials
        setState({ isLoggedIn: false });
      },
    }
  );

  // create exposed handlers
  const login = ({ email, password }) => {
    loginMutation({ variables: { email, password } });
  };
  const logout = () => {
    logoutMutation();
  };

  useEffect(() => {
    // note: it's important `verifyMutation` is only called
    //       once on load, or there'd be an infinite loop
    if (initialising) {
      setState({ isLoggedIn, initialising: false });
      verifyMutation();
    }
  }, [initialising, isLoggedIn, verifyMutation]);
  return (
    <AuthContext.Provider
      value={{
        login,
        logout,
        isLoggedIn,
        isLoading: verifying || refreshing || loggingIn || loggingOut,
      }}
      {...props}
    />
  );
};

const AlwaysLoggedInAuthProvider = (props) => {
  // state (always logged in; will require api setting too in future)
  const isLoggedIn = true;
  const isLoading = false;

  // use following exposed handlers in app code
  const login = () => {};
  const logout = () => {};

  return (
    <AuthContext.Provider
      value={{ login, logout, isLoggedIn, isLoading }}
      {...props}
    />
  );
};

const AuthProvider = env.USE_AUTHENTICATION
  ? RealAuthProvider
  : AlwaysLoggedInAuthProvider;

const useAuth = () => React.useContext(AuthContext);

export { AuthProvider, useAuth };
