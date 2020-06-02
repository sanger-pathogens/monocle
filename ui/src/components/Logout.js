import React from "react";
import { useHistory } from "react-router-dom";
import { useMutation } from "@apollo/react-hooks";
import { Grid, Box, Button } from "@material-ui/core";
import gql from "graphql-tag";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles({
  gridContainer: {
    margin: 0,
    padding: "0 24px",
    width: "100%",
    flex: "1 0 auto",
  },
});

const LOGOUT_MUTATION = gql`
  mutation Logout {
    deleteTokenCookie {
      deleted
    }
  }
`;
const Logout = () => {
  const classes = useStyles();
  let history = useHistory();
  const [logout] = useMutation(LOGOUT_MUTATION, {
    onCompleted() {
      // logged out...

      // update state
      localStorage.removeItem("isLoggedIn");

      // request credentials
      history.push("/login");
    },
  });
  const handleSubmit = (event) => {
    event.preventDefault();
    logout();
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
          <Button variant="contained" disableElevation onClick={handleSubmit}>
            Logout
          </Button>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Logout;
