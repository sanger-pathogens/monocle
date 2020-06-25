import React from "react";

import { useAuth } from "./auth";
import PageHome from "./components/PageHome";
import PageLogin from "./components/PageLogin";

const App = () => {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? <PageHome /> : <PageLogin />;
};

export default App;
