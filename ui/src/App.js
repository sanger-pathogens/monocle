import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { CssBaseline } from "@material-ui/core";
import {
  ThemeProvider,
  createMuiTheme,
  responsiveFontSizes,
} from "@material-ui/core/styles";

import "typeface-inter";

import theme from "./theme";
import PageHome from "./components/PageHome";

const generatedTheme = responsiveFontSizes(createMuiTheme(theme));

const App = () => (
  <React.Fragment>
    <CssBaseline />
    <ThemeProvider theme={generatedTheme}>
      <Router>
        <Switch>
          <Route exact path="/" component={PageHome} />
          {/* <Route path="*" component={Page404} /> */}
        </Switch>
      </Router>
    </ThemeProvider>
  </React.Fragment>
);

export default App;
