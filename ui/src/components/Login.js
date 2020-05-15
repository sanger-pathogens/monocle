import React, { useState } from "react";
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
  mutation {
    login(email: "gp16@sanger.ac.uk", password: "gp16") {
      accessToken
      refreshToken
    }
  }
`;
const Login = () => {
  const classes = useStyles();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [login, { loading, error }] = useMutation(LOGIN_MUTATION, {
    onCompleted({ login }) {
      console.log("onCompleted!");
      console.log(login);
      // document.cookie.token =
      // localStorage.setItem('token', login);
      // client.writeData({ data: { isLoggedIn: true } });
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
                <Button
                  type="submit"
                  variant="outlined"
                  color="primary"
                  style={{ textTransform: "none" }}
                >
                  Login
                </Button>
              </Box>
            </form>
          </Paper>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Login;