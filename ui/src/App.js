import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { ApolloProvider } from "@apollo/react-hooks";
import { ApolloClient } from "apollo-client";
import { InMemoryCache } from "apollo-cache-inmemory";
import { HttpLink } from "apollo-link-http";
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

const client = new ApolloClient({
  link: new HttpLink({
    uri: "http://localhost:5000/", // TODO: Move to config
    credentials: "include",
  }),
  cache: new InMemoryCache(),
});

const generatedTheme = responsiveFontSizes(createMuiTheme(theme));

const App = () => (
  <ApolloProvider client={client}>
    <CssBaseline />
    <ThemeProvider theme={generatedTheme}>
      <Router>
        <Switch>
          <Route exact path="/" component={PageHome} />
          <Route exact path="/login" component={PageLogin} />
          {/* <Route path="*" component={Page404} /> */}
        </Switch>
      </Router>
    </ThemeProvider>
  </ApolloProvider>
);

export default App;
