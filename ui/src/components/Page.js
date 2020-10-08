import React from "react";
import { Paper, Box } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import PageHeader from "./PageHeader";
import PageFooter from "./PageFooter";

const useStyles = makeStyles((theme) => ({
  page: {
    margin: 0,
    padding: 0,
    maxWidth: "100%",
    minHeight: "100vh",
    display: "flex",
    alignItems: "stretch",
    flexDirection: "column",
    background: theme.palette.primary.dark,
  },
}));

const Page = ({ hideHeader, hideFooter, children }) => {
  const classes = useStyles();
  return (
    <Paper className={classes.page}>
      {hideHeader ? null : <PageHeader />}
      {children ? <Box flexGrow={1}>{children}</Box> : null}
      {hideFooter ? null : <PageFooter />}
    </Paper>
  );
};

export default Page;
