import React from "react";

import { useAuth } from "../auth";
import { UserContext } from "../user";
import { mockUser } from "./apiMocks";

const MockUserProvider = (props) => {
  const { isLoggedIn } = useAuth();

  return (
    <UserContext.Provider value={isLoggedIn ? mockUser : null} {...props} />
  );
};

export default MockUserProvider;
