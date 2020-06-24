import React from "react";
import { AuthProvider } from "./auth";

const AppProviders = ({ children }) => <AuthProvider>{children}</AuthProvider>;

export default AppProviders;
