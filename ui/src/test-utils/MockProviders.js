import React from "react";
import { MockedProvider as ApolloProvider } from "@apollo/react-testing";
import { CssBaseline } from "@material-ui/core";
import {
  ThemeProvider,
  createMuiTheme,
  responsiveFontSizes,
} from "@material-ui/core/styles";

import "typeface-inter";

import AuthProvider from "./MockAuthProvider";
import UserProvider from "./MockUserProvider";
import theme from "../theme";
import { generateApiMocks } from "./apiMocks";

const generatedTheme = responsiveFontSizes(createMuiTheme(theme));

const AppProviders = ({
  isInitiallyLoggedIn = false,
  apiMocks = generateApiMocks().mocks,
  children,
}) => (
  <ApolloProvider mocks={apiMocks} addTypename={false}>
    <>
      <CssBaseline />
      <ThemeProvider theme={generatedTheme}>
        <AuthProvider isInitiallyLoggedIn={isInitiallyLoggedIn}>
          <UserProvider>{children}</UserProvider>
        </AuthProvider>
      </ThemeProvider>
    </>
  </ApolloProvider>
);

export default AppProviders;
