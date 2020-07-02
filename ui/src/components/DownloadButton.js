import React from "react";
import FileSaver from "file-saver";
import CloudDownloadIcon from "@material-ui/icons/CloudDownload";
import { Button } from "@material-ui/core";

// TODO: The alert was put in as a work around for cypress tests. Using filesaver creates a pop up asking where to save the file.
// This can not be blocked for the headless browser that we are using to run tests, may change in the future.
// If download testing becomes extensive may change to non-headless browser, then will need to remove the if statement here.
// Main discussion: https://github.com/cypress-io/cypress/issues/949
// Instructions on disabling pop ups: https://docs.cypress.io/api/plugins/browser-launch-api.html#Change-download-directory
const DownloadButton = ({ url, filename, children }) => {
  const handler = () => {
    if (window.Cypress) {
      alert(url.concat("," + filename));
      return;
    }
    FileSaver.saveAs(url, filename);
  };
  return (
    <Button onClick={handler} startIcon={<CloudDownloadIcon />}>
      {children}
    </Button>
  );
};

export default DownloadButton;
