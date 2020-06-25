import React, { useState } from "react";
import gql from "graphql-tag";
import { useQuery } from "@apollo/react-hooks";

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

const UserProvider = (props) => {
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

const useUser = () => React.useContext(UserContext);

export { UserProvider, useUser };
