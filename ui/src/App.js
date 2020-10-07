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
        <Route exact path="/change-password">
          <PageChangePassword />
        </Route>
        <Route path="/update">
          <PageUpdateSamples />
        </Route>
      </Switch>
    </Router>
  );
};

export default App;
