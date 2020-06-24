import React, { useState } from "react";
import gql from "graphql-tag";
import { useQuery } from "@apollo/react-hooks";

const USER_QUERY = gql`
  {
    me {
      email
      firstName
      lastName
    }
  }
`;

const UserContext = React.createContext();

const UserProvider = (props) => {
  // exposed user state
  const [user, setUser] = useState(null);

  // graphql query
  useQuery(USER_QUERY, {
    onCompleted(data) {
      // user query succeeded...

      // update state
      setUser(data.me);
    },
    onError(error) {
      // user query failed...

      // update state
      setUser(null);
    },
  });

  return <UserContext.Provider value={user} {...props} />;
};

const useUser = () => React.useContext(UserContext);

export { UserProvider, useUser };
