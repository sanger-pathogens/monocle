import React, { useState } from "react";
import fetchStream from "fetch-readablestream";
import streamSaver from "streamsaver";

import env from "./env";
import ZIP from "./zipstream";

export const DownloadingContext = React.createContext();

export const downloadsForSample = (laneId) => {
  const encodedLaneId = encodeURIComponent(laneId);
  return [
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
};

const streamDownload = (ctrl, { filename, url }) =>
  fetchStream(url).then((response) =>
    ctrl.enqueue({ name: filename, stream: () => response.body })
  );

const streamDownloads = (ctrl, downloads) =>
  Promise.all(downloads.map((d) => streamDownload(ctrl, d)));

const streamDownloadsToArchive = (archiveName, downloads) => {
  const fileStream = streamSaver.createWriteStream(archiveName);
  const readableZipStream = new ZIP({
    start() {},
    pull(ctrl) {
      return streamDownloads(ctrl, downloads).then(() => {
        ctrl.close();
      });
    },
  });
  return readableZipStream.pipeTo(fileStream);
};

export const DownloadingProvider = (props) => {
  // exposed state
  const [isDownloading, setIsDownloading] = useState(false);

  const manageDownload = async (archiveName, downloads) => {
    // TODO: The alert was put in as a work around for cypress tests. Using filesaver creates a pop up asking where to save the file.
    // This can not be blocked for the headless browser that we are using to run tests, may change in the future.
    // If download testing becomes extensive may change to non-headless browser, then will need to remove the if statement here.
    // Main discussion: https://github.com/cypress-io/cypress/issues/949
    // Instructions on disabling pop ups: https://docs.cypress.io/api/plugins/browser-launch-api.html#Change-download-directory
    if (window.Cypress) {
      alert(downloads.map((d) => d.filename).join(";"));
      return;
    }

    setIsDownloading(true);
    await streamDownloadsToArchive(archiveName, downloads);
    setIsDownloading(false);
  };

  const downloadSample = async (laneId) => {
    const archiveName = `${laneId}.zip`;
    const downloads = downloadsForSample(laneId);
    await manageDownload(archiveName, downloads);
  };

  return (
    <DownloadingContext.Provider
      value={{ isDownloading, downloadSample }}
      {...props}
    />
  );
};

export const useDownloading = () => React.useContext(DownloadingContext);
