import React from "react";
import { Grid, Box, Button } from "@material-ui/core";
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

const Logout = () => {
  const classes = useStyles();

  // global auth actions
  const { logout } = useAuth();

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
