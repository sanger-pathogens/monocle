import React from "react";
import { Router, Switch, Route } from "react-router-dom";
import { ApolloProvider } from "@apollo/react-hooks";
import { CssBaseline } from "@material-ui/core";
import {
  ThemeProvider,
  createMuiTheme,
  responsiveFontSizes,
} from "@material-ui/core/styles";

import "typeface-inter";

import theme from "./theme";
import PageHome from "./components/PageHome";
import PageLogin from "./components/PageLogin";
import PageMe from "./components/PageMe";
import AuthRoute from "./components/AuthRoute";
import history from "./history";
import client from "./client";

const generatedTheme = responsiveFontSizes(createMuiTheme(theme));

const App = () => (
  <ApolloProvider client={client}>
    <CssBaseline />
    <ThemeProvider theme={generatedTheme}>
      <Router history={history}>
        <Switch>
          <Route exact path="/" component={PageHome} />
          <Route exact path="/login" component={PageLogin} />
          <AuthRoute exact path="/me" component={PageMe} />
          {/* <Route path="*" component={Page404} /> */}
        </Switch>
      </Router>
    </ThemeProvider>
  </ApolloProvider>
);

export default App;
