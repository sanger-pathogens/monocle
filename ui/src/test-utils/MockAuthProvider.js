import React, { useState } from "react";

import { AuthContext } from "../auth";

const MockAuthProvider = ({ isInitiallyLoggedIn = false, ...rest }) => {
  // use `isLoggedIn` within app code, but load
  // initial value from local storage to persist
  // between refreshes
  const [isLoggedIn, setIsLoggedIn] = useState(isInitiallyLoggedIn);

  // use following exposed handlers in app code
  const login = () => setIsLoggedIn(true);
  const logout = () => setIsLoggedIn(false);

  return (
    <AuthContext.Provider value={{ login, logout, isLoggedIn }} {...rest} />
  );
};

export default MockAuthProvider;
