import React from "react";
import { useQuery } from "@apollo/react-hooks";
import gql from "graphql-tag";
import { Paper, Grid, Box, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles({
  gridContainer: {
    margin: 0,
    padding: "0 24px",
    width: "100%",
    flex: "1 0 auto",
  },
});

const ME_QUERY = gql`
  {
    me {
      email
      firstName
      lastName
    }
  }
`;

const Me = () => {
  const classes = useStyles();
  const { loading, error, data } = useQuery(ME_QUERY);
  console.log(data);

  let me = null;
  if (data && !(loading || error)) {
    // TODO: Handle loading/error cases
    me = data.me ? data.me : null;
  }
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
            <Box p={4}>
              {me ? (
                <Grid container>
                  <Grid item xs={6}>
                    <Typography>Email</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography>{me.email}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography>First Name</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography>{me.firstName}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography>Last Name</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography>{me.lastName}</Typography>
                  </Grid>
                </Grid>
              ) : null}
            </Box>
          </Paper>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Me;
