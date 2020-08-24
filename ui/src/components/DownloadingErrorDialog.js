import React, { useEffect } from "react";
import {
  Button,
  Dialog,
  DialogTitle,
  DialogActions,
  DialogContent,
  DialogContentText,
} from "@material-ui/core";

import { useDownloading } from "../downloading";

const DownloadingErrorDialog = () => {
  const { error } = useDownloading();
  const [open, setOpen] = React.useState(false);

  useEffect(() => {
    if (error) {
      setOpen(true);
    }
  }, [error]);

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">{"Download error"}</DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">
          An error occurred whilst attempting to download data files.
          <br />
          The actual error message was: <i>{error ? error.message : error}</i>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="primary" autoFocus>
          Ok
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DownloadingErrorDialog;
