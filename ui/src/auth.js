import React, { useState } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";

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

const AuthContext = React.createContext();

const AuthProvider = (props) => {
  // use `isLoggedIn` within app code, but load
  // initial value from local storage to persist
  // between refreshes
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") !== null
  );

  // graphql mutations for login, logout
  const [loginMutation] = useMutation(LOGIN_MUTATION, {
    onCompleted() {
      // login succeeded...
      localStorage.setItem("isLoggedIn", "yes");
      setIsLoggedIn(true);
    },
    onError() {
      // login failed...
      localStorage.removeItem("isLoggedIn");
      setIsLoggedIn(false);
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
  const login = ({ email, password }) =>
    loginMutation({ variables: { email, password } });
  const logout = () => logoutMutation();

  return (
    <AuthContext.Provider value={{ login, logout, isLoggedIn }} {...props} />
  );
};

const useAuth = () => React.useContext(AuthContext);

export { AuthProvider, useAuth };
