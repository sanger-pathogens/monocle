import React, { useState } from "react";
import { Box, Typography, TextField, Paper, Button } from "@material-ui/core";
import { Alert } from "@material-ui/lab";
import { makeStyles } from "@material-ui/core/styles";

import { useAuth } from "../auth";

const useStyles = makeStyles({
  login: {
    maxWidth: "400px",
    margin: "8px",
  },
});

const Login = () => {
  const classes = useStyles();

  // global auth actions
  const { login, loginError } = useAuth();

  // user credentials for form
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // on form submit
  const handleSubmit = (event) => {
    event.preventDefault();
    login({ email, password });
  };

  return (
    <Paper className={classes.login}>
      <form onSubmit={handleSubmit}>
        <Box p={4}>
          <Typography variant="h4" align="center" gutterBottom>
            Monocle
          </Typography>
          {loginError ? (
            <Alert severity="error" elevation={0} variant="filled">
              {loginError}
            </Alert>
          ) : null}
          <TextField
            id="Email"
            label="email"
            type="email"
            fullWidth
            autoFocus
            required
            value={email}
            onInput={(e) => setEmail(e.target.value)}
          />
          <TextField
            id="password"
            label="password"
            type="password"
            fullWidth
            required
            value={password}
            onInput={(e) => setPassword(e.target.value)}
          />
          <Box pt={4} align="right">
            <Button
              type="submit"
              variant="contained"
              disableElevation
              style={{ textTransform: "none" }}
            >
              Login
            </Button>
          </Box>
        </Box>
      </form>
    </Paper>
  );
};

export default Login;
