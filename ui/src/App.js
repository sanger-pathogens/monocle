import React from "react";

import { useAuth } from "./auth";
import AuthenticatedApp from "./AuthenticatedApp";
import UnauthenticatedApp from "./UnauthenticatedApp";

const App = () => {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? <AuthenticatedApp /> : <UnauthenticatedApp />;
};

export default App;
