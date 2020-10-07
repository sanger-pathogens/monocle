import React from "react";
import { Link } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Button,
  useScrollTrigger,
  Typography,
  Menu,
  MenuItem,
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
  const { user } = useUser();

  const [anchorEl, setAnchorEl] = React.useState(null);
  const isMenuOpen = Boolean(anchorEl);

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const renderMenu = (
    <Menu
      anchorEl={anchorEl}
      anchorOrigin={{ vertical: "top", horizontal: "right" }}
      keepMounted
      transformOrigin={{ vertical: "top", horizontal: "right" }}
      open={isMenuOpen}
      onClose={handleProfileMenuClose}
    >
      <MenuItem component={Link} to="/change-password">
        Change Password
      </MenuItem>
      <MenuItem onClick={logout}>Logout</MenuItem>
    </Menu>
  );

  return (
    <React.Fragment>
      <AppBar
        position="fixed"
        color={trigger ? "primary" : "transparent"}
        style={{ borderBottom: trigger ? "2px solid white" : "none" }}
        elevation={0}
      >
        <Toolbar variant="dense">
          {/* title/home button */}
          <Button id="buttonHome" color="default" to="/" component={Link}>
            Monocle
          </Button>

          {/* fill horizontally */}
          <div className={classes.grow} />

          {/* user profile */}
          {user ? (
            <Button id="buttonProfileMenu" onClick={handleProfileMenuOpen}>
              <AccountCircle className={classes.accountIcon} />
              <Typography variant="button">
                {user.firstName} {user.lastName}
              </Typography>
            </Button>
          ) : null}
        </Toolbar>
      </AppBar>

      {/* user profile menu */}
      {renderMenu}
    </React.Fragment>
  );
};

export default Header;
