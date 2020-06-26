import React from "react";
import FileSaver from "file-saver";
import CloudDownloadIcon from "@material-ui/icons/CloudDownload";
import { Button } from "@material-ui/core";

const DownloadButton = ({ url, filename, children }) => {
  const handler = () => {
    FileSaver.saveAs(url, filename);
  };
  return (
    <Button onClick={handler} startIcon={<CloudDownloadIcon />}>
      {children}
    </Button>
  );
};

export default DownloadButton;
