import React from "react";
import {
  AppBar,
  Toolbar,
  Button,
  Link,
  useScrollTrigger,
  Typography,
} from "@material-ui/core";
import { AccountCircle } from "@material-ui/icons";
import { makeStyles } from "@material-ui/core/styles";

import { useAuth } from "../auth";
import { useUser } from "../user";

const useStyles = makeStyles((theme) => ({
  grow: {
    flexGrow: 1,
  },
  accountIcon: {
    paddingRight: 4,
  },
  user: {
    display: "flex",
    position: "relative",
    marginRight: 4,
    paddingRight: 12,
    borderRight: "2px solid white",
  },
  toolbarIcon: {
    padding: theme.spacing(0, 2),
    height: "100%",
    position: "absolute",
    pointerEvents: "none",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
}));

const Header = () => {
  const classes = useStyles();
  const trigger = useScrollTrigger({
    disableHysteresis: true,
    threshold: 0,
    target: window,
  });
  const { logout } = useAuth();
  const { user, getUser } = useUser();

  return (
    <AppBar
      position="fixed"
      color={trigger ? "primary" : "transparent"}
      style={{ borderBottom: trigger ? "2px solid white" : "none" }}
      elevation={0}
    >
      <Toolbar variant="dense">
        <Button id="buttonHome" color="inherit" href="/" component={Link}>
          Monocle
        </Button>
        <div className={classes.grow} />
        <Button color="inherit" onClick={getUser}>
          Fetch User
        </Button>
        {user ? (
          <div className={classes.user}>
            <AccountCircle className={classes.accountIcon} />
            <Typography variant="button">
              {user.firstName} {user.lastName}
            </Typography>
          </div>
        ) : null}
        <Button id="buttonLogout" color="inherit" onClick={() => logout()}>
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
