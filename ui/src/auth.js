import React, { useState } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";

import history from "./history";

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
  // exposed boolean login state to avoid reading
  // from local storage in app
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") !== null
  );

  // graphql mutations for login, logout
  const [loginMutation] = useMutation(LOGIN_MUTATION, {
    onCompleted(data) {
      // login succeeded...

      // update state
      localStorage.setItem("isLoggedIn", "yes");
      setIsLoggedIn(true);

      // go to private page
      history.push("/me");
    },
    onError(error) {
      // login failed...

      // update state
      localStorage.removeItem("isLoggedIn");
      setIsLoggedIn(false);

      // redirect to request credentials
      history.push("/login");
    },
  });
  const [logoutMutation] = useMutation(LOGOUT_MUTATION, {
    onCompleted() {
      // logout succeeded...

      // update state
      localStorage.removeItem("isLoggedIn");

      // redirect to request credentials
      history.push("/login");
    },
  });

  // exposed handlers
  const login = ({ email, password }) =>
    loginMutation({ variables: { email, password } });
  const logout = () => logoutMutation();

  return (
    <AuthContext.Provider value={{ login, logout, isLoggedIn }} {...props} />
  );
};

const useAuth = () => React.useContext(AuthContext);

export { AuthProvider, useAuth };
