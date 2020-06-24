import React from "react";

import PageHome from "./components/PageHome";
import { UserProvider } from "./user";

const AuthenticatedApp = () => (
  <UserProvider>
    <PageHome />
  </UserProvider>
);

export default AuthenticatedApp;
