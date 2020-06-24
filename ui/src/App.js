import React from "react";

import { useAuth } from "./auth";
import AuthenticatedApp from "./AuthenticatedApp";
import PageLogin from "./components/PageLogin";

const App = () => {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? <AuthenticatedApp /> : <PageLogin />;
};

export default App;
