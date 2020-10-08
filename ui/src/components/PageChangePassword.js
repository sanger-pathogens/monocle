import React from "react";
import { Box } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import Page from "./Page";
import Footer from "./PageFooter";
import ChangePassword from "./ChangePassword";

const useStyles = makeStyles({
  container: {
    flex: 1,
    display: "flex",
    maxWidth: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
});

const PageChangePassword = () => {
  const classes = useStyles();
  return (
    <Page header={null} footer={<Footer />}>
      <Box className={classes.container}>
        <ChangePassword />
      </Box>
    </Page>
  );
};

export default PageChangePassword;
