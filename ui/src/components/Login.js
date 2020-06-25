import React, { useState } from "react";
import {
  Grid,
  Box,
  Typography,
  TextField,
  Paper,
  Button,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import { useAuth } from "../auth";

const useStyles = makeStyles({
  gridContainer: {
    margin: 0,
    padding: "0 24px",
    width: "100%",
    flex: "1 0 auto",
  },
});

const Login = () => {
  const classes = useStyles();

  // global auth actions
  const { login } = useAuth();

  // user credentials for form
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // on form submit
  const handleSubmit = (event) => {
    event.preventDefault();
    login({ email, password });
  };

  return (
    <Grid
      container
      justify="center"
      spacing={1}
      className={classes.gridContainer}
    >
      <Grid item xs={12} sm={8} md={6} lg={4}>
        <Box pt={8}>
          <Paper>
            <form onSubmit={handleSubmit}>
              <Box p={4}>
                <Typography variant="h4" align="center" gutterBottom>
                  Monocle
                </Typography>
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
                  label="Password"
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
                    Log In
                  </Button>
                </Box>
              </Box>
            </form>
          </Paper>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Login;
