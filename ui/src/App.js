import React from "react";

import { useAuth } from "./auth";
import PageHome from "./components/PageHome";
import PageLogin from "./components/PageLogin";

const App = () => {
  const { isLoggedIn, isLoading } = useAuth();
  return isLoading ? null : isLoggedIn ? <PageHome /> : <PageLogin />;
};

export default App;
