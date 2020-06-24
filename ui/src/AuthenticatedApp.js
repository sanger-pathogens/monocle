import React from "react";
import { Router, Switch, Route } from "react-router-dom";

import PageHome from "./components/PageHome";
import PageLogin from "./components/PageLogin";
import PageMe from "./components/PageMe";
import AuthRoute from "./components/AuthRoute";
import history from "./history";

const AuthenticatedApp = () => (
  <Router history={history}>
    <Switch>
      <Route exact path="/" component={PageHome} />
      <Route exact path="/login" component={PageLogin} />
      <AuthRoute exact path="/me" component={PageMe} />
      {/* <Route path="*" component={Page404} /> */}
    </Switch>
  </Router>
);

export default AuthenticatedApp;
