import React from "react";
import { ApolloProvider } from "@apollo/react-hooks";
import { CssBaseline } from "@material-ui/core";
import {
  ThemeProvider,
  createMuiTheme,
  responsiveFontSizes,
} from "@material-ui/core/styles";

import "typeface-inter";

import { AuthProvider } from "./auth";
import { UserProvider } from "./user";
import { DownloadingProvider } from "./downloading";
import client from "./client";
import theme from "./theme";

const generatedTheme = responsiveFontSizes(createMuiTheme(theme));

const AppProviders = ({ children }) => (
  <ApolloProvider client={client}>
    <CssBaseline />
    <ThemeProvider theme={generatedTheme}>
      <AuthProvider>
        <UserProvider>
          <DownloadingProvider>{children}</DownloadingProvider>
        </UserProvider>
      </AuthProvider>
    </ThemeProvider>
  </ApolloProvider>
);

export default AppProviders;
