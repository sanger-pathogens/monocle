import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import { useAuth } from "./auth";
import PageChangePassword from "./components/PageChangePassword";
import PageHome from "./components/PageHome";
import PageLogin from "./components/PageLogin";
import PageUpdateSamples from "./components/PageUpdateSamples";

const App = () => {
  const { isLoggedIn, isLoading } = useAuth();

  return (
    <Router>
      <Switch>
        <Route exact path="/">
          {isLoading ? null : isLoggedIn ? <PageHome /> : <PageLogin />}
        </Route>
        <Route path="/change-password">
          {isLoading ? null : isLoggedIn ? <PageChangePassword /> : <PageLogin />}
        </Route>
        <Route path="/update">
          {isLoading ? null : isLoggedIn ? <PageUpdateSamples /> : <PageLogin />}
        </Route>
      </Switch>
    </Router>
  );
};

export default App;
