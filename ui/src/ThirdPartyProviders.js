import React from "react";
import { ApolloProvider } from "@apollo/react-hooks";
import { CssBaseline } from "@material-ui/core";
import {
  ThemeProvider,
  createMuiTheme,
  responsiveFontSizes,
} from "@material-ui/core/styles";

import "typeface-inter";

import client from "./client";
import theme from "./theme";

const generatedTheme = responsiveFontSizes(createMuiTheme(theme));

const ThirdPartyProviders = ({ children }) => (
  <ApolloProvider client={client}>
    <CssBaseline />
    <ThemeProvider theme={generatedTheme}>{children}</ThemeProvider>
  </ApolloProvider>
);

export default ThirdPartyProviders;
