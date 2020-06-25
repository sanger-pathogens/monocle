import React from "react";
import { Paper } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  page: {
    margin: 0,
    padding: 0,
    minHeight: "100vh",
    display: "flex",
    alignItems: "stretch",
    flexDirection: "column",
    background: theme.palette.primary.dark,
  },
  content: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
}));

const Page = ({ header, footer, children }) => {
  const classes = useStyles();
  return (
    <Paper className={classes.page}>
      {header ? header : null}
      {children ? <div className={classes.content}>{children}</div> : null}
      {footer ? footer : null}
    </Paper>
  );
};

export default Page;
