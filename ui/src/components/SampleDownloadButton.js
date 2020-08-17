import React from "react";
import streamSaver from "streamsaver";
import { Button } from "@material-ui/core";
import { CloudDownload } from "@material-ui/icons";

import env from "../env";
import ZIP from "../zipstream";
import { useDownloading } from "../downloading";

// see https://github.com/jimmywarting/StreamSaver.js/blob/master/examples/saving-multiple-files.html

const handlerGenerator = (laneId, setIsDownloading) => {
  const encodedLaneId = encodeURIComponent(laneId);
  const archiveName = `${laneId}.zip`;
  const downloads = [
    {
      filename: `${laneId}_1.fastq.gz`,
      url: `${env.API_ROOT_URL}read1/${encodedLaneId}`,
    },
    {
      filename: `${laneId}_2.fastq.gz`,
      url: `${env.API_ROOT_URL}read2/${encodedLaneId}`,
    },
    {
      filename: `${laneId}.fa`,
      url: `${env.API_ROOT_URL}assembly/${encodedLaneId}`,
    },
    {
      filename: `${laneId}.gff`,
      url: `${env.API_ROOT_URL}annotation/${encodedLaneId}`,
    },
  ];
  const handler = () => {
    // TODO: The alert was put in as a work around for cypress tests. Using filesaver creates a pop up asking where to save the file.
    // This can not be blocked for the headless browser that we are using to run tests, may change in the future.
    // If download testing becomes extensive may change to non-headless browser, then will need to remove the if statement here.
    // Main discussion: https://github.com/cypress-io/cypress/issues/949
    // Instructions on disabling pop ups: https://docs.cypress.io/api/plugins/browser-launch-api.html#Change-download-directory
    if (window.Cypress) {
      alert(downloads.map((d) => d.filename).join(";"));
      return;
    }

    // disable other downloads
    setIsDownloading(true);

    const fileStream = streamSaver.createWriteStream(archiveName);
    const readableZipStream = new ZIP({
      start() {},
      async pull(ctrl) {
        // asynchronously fetch all files
        // (browser should parallelise requests in batches)
        await Promise.all(
          downloads.map(async (d) => {
            // run the download
            const response = await fetch(d.url);

            // add to archive
            const name = d.filename;
            const stream = () => response.body;
            ctrl.enqueue({ name, stream });
          })
        );

        // done adding all files
        ctrl.close();
      },
    });

    // more optimized
    if (window.WritableStream && readableZipStream.pipeTo) {
      return readableZipStream.pipeTo(fileStream).then(() => {
        // allow further downloads
        setIsDownloading(false);
      });
    }

    // less optimized
    const writer = fileStream.getWriter();
    const reader = readableZipStream.getReader();
    const pump = () =>
      reader
        .read()
        .then((res) =>
          res.done ? writer.close() : writer.write(res.value).then(pump)
        );

    pump();

    // allow further downloads
    setIsDownloading(false);
  };

  return handler;
};

const SampleDownloadButton = ({ laneId }) => {
  const { isDownloading, setIsDownloading } = useDownloading();
  return (
    <Button
      onClick={handlerGenerator(laneId, setIsDownloading)}
      startIcon={<CloudDownload />}
      disabled={isDownloading}
    >
      {laneId}
    </Button>
  );
};

export default SampleDownloadButton;
