import React from "react";
import { Paper } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  page: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    margin: 0,
    width: "100%",
    background: theme.palette.primary.dark,
  },
}));

const Page = ({ header, footer, children }) => {
  const classes = useStyles();
  return (
    <Paper className={classes.page}>
      {header ? header : null}
      {children}
      {footer ? footer : null}
    </Paper>
  );
};

export default Page;
