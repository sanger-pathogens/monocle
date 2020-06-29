import React, { useState } from "react";
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

export const AuthContext = React.createContext();

const RealAuthProvider = (props) => {
  // use `isLoggedIn` within app code, but load
  // initial value from local storage to persist
  // between refreshes
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") !== null
  );
  const [loginError, setLoginError] = useState(null);
  const [loginLoading, setLoginLoading] = useState(false);

  // graphql mutations for login, logout
  const [loginMutation] = useMutation(LOGIN_MUTATION, {
    onCompleted() {
      // login succeeded...
      localStorage.setItem("isLoggedIn", "yes");
      setIsLoggedIn(true);
      setLoginLoading(false);
    },
    onError(error) {
      // login failed...
      localStorage.removeItem("isLoggedIn");
      setIsLoggedIn(false);
      setLoginLoading(false);
      setLoginError(error.message);
    },
  });
  const [logoutMutation] = useMutation(LOGOUT_MUTATION, {
    onCompleted() {
      // logout succeeded...
      localStorage.removeItem("isLoggedIn");
      setIsLoggedIn(false);
    },
    onError() {
      // logout failed...
      // (could happen if API not reachable,
      //  but cookies will still time out)
      localStorage.removeItem("isLoggedIn");
      setIsLoggedIn(false);
    },
  });

  // use following exposed handlers in app code
  const login = ({ email, password }) => {
    setLoginError(null);
    setLoginLoading(true);
    loginMutation({ variables: { email, password } });
  };

  const logout = () => logoutMutation();

  return (
    <AuthContext.Provider
      value={{ login, logout, isLoggedIn, loginError, loginLoading }}
      {...props}
    />
  );
};

const AlwaysLoggedInAuthProvider = (props) => {
  // state (always logged in; will require api setting too in future)
  const [isLoggedIn] = useState(true);

  // use following exposed handlers in app code
  const login = () => {};
  const logout = () => {};

  return (
    <AuthContext.Provider value={{ login, logout, isLoggedIn }} {...props} />
  );
};

const AuthProvider = env.USE_AUTHENTICATION
  ? RealAuthProvider
  : AlwaysLoggedInAuthProvider;

const useAuth = () => React.useContext(AuthContext);

export { AuthProvider, useAuth };
