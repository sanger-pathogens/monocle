import React from "react";

import { useAuth } from "../auth";
import { UserContext } from "../user";
import { mockUser } from "./apiMocks";

const MockUserProvider = (props) => {
  const { isLoggedIn } = useAuth();

  return (
    <UserContext.Provider
      value={{ user: isLoggedIn ? mockUser : null, getUser: () => {} }}
      {...props}
    />
  );
};

export default MockUserProvider;
