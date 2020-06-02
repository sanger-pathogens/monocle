import * as React from "react";
import { Route, Redirect } from "react-router-dom";

const AuthRoute = (props) =>
  localStorage.getItem("isLoggedIn") === null ? (
    <Redirect to={`/login`} />
  ) : (
    <Route {...props} />
  );

export default AuthRoute;
