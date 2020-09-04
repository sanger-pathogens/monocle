import React, { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Modal from "@material-ui/core/Modal";
import { Button, Link } from "@material-ui/core";

function getModalStyle() {
  const top = 50;
  const left = 50;

  return {
    top: `${top}%`,
    left: `${left}%`,
    transform: `translate(-${top}%, -${left}%)`,
  };
}

const useStyles = makeStyles((theme) => ({
  paper: {
    position: "absolute",
    width: 400,
    backgroundColor: theme.palette.background.paper,
    border: "2px solid #000",
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 2, 3),
    color: "white",
  },
}));

function CommitModal({ showModal, setIsCommitted, isCommitted }) {
  const classes = useStyles();
  const [modalStyle] = useState(getModalStyle);

  const handleClose = () => {
    const showModal = false;
    setIsCommitted(null);
  };

  const bodyCommitSuccess = (
    <div style={modalStyle} className={classes.paper}>
      <h2 id="simple-modal-title">Updated</h2>
      <p id="simple-modal-description">
        Your commit was successful! Click okay to return to the home page or
        cancel to upload another spreadsheet.
      </p>
      <Button onClick={handleClose} href="/" component={Link}>
        Okay
      </Button>
      <Button onClick={handleClose} href="/update" component={Link}>
        Cancel
      </Button>
      <CommitModal />
    </div>
  );

  const bodyCommitFail = (
    <div style={modalStyle} className={classes.paper}>
      <h2 id="simple-modal-title">Updated</h2>
      <p id="simple-modal-description">
        Something went wrong and your commit failed! Click okay to try again
        with a new spreadsheet or cancel return to the home page.
      </p>
      <Button onClick={handleClose} href="/update" component={Link}>
        Okay
      </Button>
      <Button onClick={handleClose} href="/" component={Link}>
        Cancel
      </Button>
      <CommitModal />
    </div>
  );

  return (
    <div>
      <Modal
        open={showModal}
        onClose={handleClose}
        aria-labelledby="simple-modal-title"
        aria-describedby="simple-modal-description"
      >
        {isCommitted === true ? bodyCommitSuccess : bodyCommitFail}
      </Modal>
    </div>
  );
}

export default CommitModal;
