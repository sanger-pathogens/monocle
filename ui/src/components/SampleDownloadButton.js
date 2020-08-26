import React from "react";
import { Button } from "@material-ui/core";
import { CloudDownload } from "@material-ui/icons";

import { useDownloading } from "../downloading";

const SampleDownloadButton = ({ laneId }) => {
  const { isDownloading, downloadSample } = useDownloading();
  const handler = () => {
    downloadSample(laneId);
  };
  return (
    <Button
      onClick={handler}
      startIcon={<CloudDownload />}
      disabled={isDownloading}
    >
      {laneId}
    </Button>
  );
};

export default SampleDownloadButton;
