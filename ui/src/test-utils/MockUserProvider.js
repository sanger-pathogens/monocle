import React from "react";

import { UserContext } from "../user";

const mockUser = {
  email: "admin@juno.com",
  firstName: "Luke",
  lastName: "Skywalker",
};

const MockUserProvider = (props) => {
  const { isLoggedIn } = useAuth();

  return (
    <UserContext.Provider value={isLoggedIn ? mockUser : null} {...props} />
  );
};

export default MockUserProvider;
