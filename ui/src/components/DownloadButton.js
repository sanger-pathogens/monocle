import React from "react";
import FileSaver from "file-saver";
import streamSaver from "streamsaver";
import CloudDownloadIcon from "@material-ui/icons/CloudDownload";
import { Button } from "@material-ui/core";

const DownloadButton = ({ url, filename, children }) => {
  const handler = async () => {
    // TODO: The alert was put in as a work around for cypress tests. Using filesaver creates a pop up asking where to save the file.
    // This can not be blocked for the headless browser that we are using to run tests, may change in the future.
    // If download testing becomes extensive may change to non-headless browser, then will need to remove the if statement here.
    // Main discussion: https://github.com/cypress-io/cypress/issues/949
    // Instructions on disabling pop ups: https://docs.cypress.io/api/plugins/browser-launch-api.html#Change-download-directory
    if (window.Cypress) {
      alert(url.concat("," + filename));
      return;
    }

    // FileSaver method is simple, but loads all into memory,
    // so not ideal for larger files
    // FileSaver.saveAs(url, filename);

    // use web streams and pipe to file
    // see https://github.com/jimmywarting/StreamSaver.js/blob/master/examples/fetch.html
    fetch(url).then((res) => {
      const size = res.headers.get("content-length");
      const readableStream = res.body;

      // specifying size indicates download is occurring
      const fileStream = streamSaver.createWriteStream(filename, { size });

      // more optimized
      if (window.WritableStream && readableStream.pipeTo) {
        return readableStream
          .pipeTo(fileStream)
          .then(() => console.log("done writing"));
      }

      const writer = fileStream.getWriter();
      const reader = res.body.getReader();
      const pump = () =>
        reader
          .read()
          .then((res) =>
            res.done ? writer.close() : writer.write(res.value).then(pump)
          );

      pump();
    });
  };
  return (
    <Button onClick={handler} startIcon={<CloudDownloadIcon />}>
      {children}
    </Button>
  );
};

export default DownloadButton;
