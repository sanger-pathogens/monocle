import React from "react";
import FileSaver from "file-saver";
      
const downloadLaneData = (laneId, laneId_encoded) => {
    FileSaver.saveAs(`${window.env.DOWNLOAD_ROOT_URL}${laneId_encoded}`,`${laneId}.tar.gz`);
};

const handlerGenerator = (laneId) => {
    let laneId_encoded =`${encodeURIComponent(`${laneId}`)}`
    return () => downloadLaneData(laneId, laneId_encoded);
};

export default handlerGenerator;
