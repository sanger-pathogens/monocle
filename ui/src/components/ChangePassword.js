import React, { useState } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";
import { Box, Typography, TextField, Paper, Button } from "@material-ui/core";
import { Alert } from "@material-ui/lab";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles({
  login: {
    maxWidth: "400px",
    margin: "8px",
  },
});

const CHANGE_PASSWORD_MUTATION = gql`
  mutation ChangePassword($oldPassword: String!, $newPassword: String!) {
    changePassword(oldPassword: $oldPassword, newPassword: $newPassword) {
      committed
    }
  }
`;

const ChangePassword = () => {
  const classes = useStyles();

  const [changePasswordMutation, { error }] = useMutation(
    CHANGE_PASSWORD_MUTATION
  );
  const changePassword = ({ oldPassword, newPassword }) => {
    changePasswordMutation({ variables: { oldPassword, newPassword } });
  };

  // user credentials for form
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  // on form submit
  const handleSubmit = (event) => {
    event.preventDefault();
    changePassword({ oldPassword, newPassword });
  };

  return (
    <Paper className={classes.login}>
      <form onSubmit={handleSubmit}>
        <Box p={4}>
          <Typography variant="h4" align="center" gutterBottom>
            Monocle
          </Typography>
          {error ? (
            <Alert severity="error" elevation={0} variant="filled">
              {error}
            </Alert>
          ) : null}
          <TextField
            id="oldPassword"
            label="oldPassword"
            type="password"
            fullWidth
            required
            value={oldPassword}
            onInput={(e) => setOldPassword(e.target.value)}
          />
          <TextField
            id="newPassword"
            label="newPassword"
            type="password"
            fullWidth
            required
            value={newPassword}
            onInput={(e) => setNewPassword(e.target.value)}
          />
          <Box pt={4} align="right">
            <Button
              type="submit"
              variant="contained"
              disableElevation
              style={{ textTransform: "none" }}
            >
              Change Password
            </Button>
          </Box>
        </Box>
      </form>
    </Paper>
  );
};

export default ChangePassword;
