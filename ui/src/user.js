import React, { useState } from "react";
import gql from "graphql-tag";
import { useQuery } from "@apollo/react-hooks";

import env from "./env";
import { useAuth } from "./auth";

export const USER_QUERY = gql`
  {
    me {
      email
      firstName
      lastName
    }
  }
`;

export const UserContext = React.createContext();

const RealUserProvider = (props) => {
  const { isLoggedIn } = useAuth();

  // exposed user state
  const [user, setUser] = useState(null);

  // graphql query
  const skip = !isLoggedIn;
  useQuery(USER_QUERY, {
    onCompleted(data) {
      // user query succeeded...

      // handle apollo bug: see https://github.com/apollographql/react-apollo/issues/3943
      if (skip) {
        return;
      }

      // update state
      setUser(data.me);
    },
    onError() {
      // user query failed...

      // update state
      setUser(null);
    },
    skip: !isLoggedIn,
  });

  return <UserContext.Provider value={user} {...props} />;
};

const AlwaysLoggedInUserProvider = (props) => {
  // exposed user state
  const [user] = useState({
    email: "admin@sanger.ac.uk",
    firstName: "Fake",
    lastName: "User",
  });

  return <UserContext.Provider value={user} {...props} />;
};

const UserProvider = env.USE_AUTHENTICATION
  ? RealUserProvider
  : AlwaysLoggedInUserProvider;

const useUser = () => React.useContext(UserContext);

export { UserProvider, useUser };
