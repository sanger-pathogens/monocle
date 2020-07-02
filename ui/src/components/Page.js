import React from "react";
import { Paper } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

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

const Page = ({ header, footer, children }) => {
  const classes = useStyles();
  return (
    <Paper className={classes.page}>
      {header ? header : null}
      {children ? children : null}
      {footer ? footer : null}
    </Paper>
  );
};

export default Page;
