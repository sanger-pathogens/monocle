import React from "react";
import streamSaver from "streamsaver";
import CloudDownloadIcon from "@material-ui/icons/CloudDownload";
import { Button } from "@material-ui/core";

import env from "../env";
import ZIP from "../zipstream";

// see https://github.com/jimmywarting/StreamSaver.js/blob/master/examples/saving-multiple-files.html

const handlerGenerator = (laneId) => {
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
    const fileStream = streamSaver.createWriteStream(archiveName);
    const readableZipStream = new ZIP({
      start(ctrl) {},
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
      return readableZipStream
        .pipeTo(fileStream)
        .then(() => console.log("done writing"));
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
  };

  return handler;
};

const SampleDownloadButton = ({ laneId }) => {
  return (
    <Button
      onClick={handlerGenerator(laneId)}
      startIcon={<CloudDownloadIcon />}
    >
      {laneId}
    </Button>
  );
};

export default SampleDownloadButton;
