import React from "react";
import { Router, Switch, Route } from "react-router-dom";

import PageHome from "./components/PageHome";
import PageLogin from "./components/PageLogin";
import PageMe from "./components/PageMe";
import history from "./history";
import { UserProvider } from "./user";

const AuthenticatedApp = () => (
  <UserProvider>
    <Router history={history}>
      <Switch>
        <Route exact path="/" component={PageHome} />
        <Route exact path="/me" component={PageMe} />
        {/* <Route path="*" component={Page404} /> */}
      </Switch>
    </Router>
  </UserProvider>
);

export default AuthenticatedApp;
