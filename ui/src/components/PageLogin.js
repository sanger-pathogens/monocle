import React from "react";
import { Box } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import Page from "./Page";
import Footer from "./Footer";
import Login from "./Login";

const useStyles = makeStyles({
  container: {
    flex: 1,
    display: "flex",
    maxWidth: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
});

const PageLogin = () => {
  const classes = useStyles();
  return (
    <Page header={null} footer={<Footer />}>
      <Box className={classes.container}>
        <Login />
      </Box>
    </Page>
  );
};

export default PageLogin;
