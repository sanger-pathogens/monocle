import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import { IconButton } from "@material-ui/core";
import { CloudDownload } from "@material-ui/icons";

import { useDownloading } from "../downloading";

const useStyles = makeStyles((theme) => ({
  margin: {
    margin: theme.spacing(1),
  },
}));

const SampleDownloadButton = ({ laneId }) => {
  const classes = useStyles();
  const { isDownloading, downloadSample } = useDownloading();
  const handler = () => {
    downloadSample(laneId);
  };
  return (
    <IconButton
      className={classes.margin}
      onClick={handler}
      disabled={isDownloading}
      size="small"
      aria-label={laneId}
    >
      <CloudDownload fontSize="inherit" />
    </IconButton>
  );
};

export default SampleDownloadButton;
