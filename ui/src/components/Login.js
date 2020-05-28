import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import { useMutation } from "@apollo/react-hooks";
import {
  Grid,
  Box,
  Typography,
  TextField,
  Paper,
  Button,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import gql from "graphql-tag";

const useStyles = makeStyles({
  gridContainer: {
    margin: 0,
    padding: "0 24px",
    width: "100%",
    flex: "1 0 auto",
  },
});

const LOGIN_MUTATION = gql`
  mutation Login($email: String!, $password: String!) {
    tokenAuth(email: $email, password: $password) {
      token
    }
  }
`;
const Login = () => {
  const classes = useStyles();
  let history = useHistory();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [login, { loading, error, data }] = useMutation(LOGIN_MUTATION, {
    onCompleted(data) {
      // change page
      history.push("/me");
    },
  });
  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(email, password);
    login({ variables: { email, password } });
  };

  return (
    <Grid
      container
      justify="center"
      spacing={1}
      className={classes.gridContainer}
    >
      <Grid item xs={12} md={6} lg={4}>
        <Box pt={8}>
          <Paper>
            <form onSubmit={handleSubmit}>
              <Box p={4}>
                <Typography variant="h2" gutterBottom>
                  Login
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
                <Box pt={4}>
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
        </Box>
      </Grid>
    </Grid>
  );
};

export default Login;
