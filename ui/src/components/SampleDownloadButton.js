import React from "react";

      
const downloadLaneData = (laneId, laneId_encoded) =>
    fetch(`http://127.0.0.1:8000/${laneId_encoded}`).then((response) => {
    response.blob().then((blob) => {
      let url = window.URL.createObjectURL(blob);
      let a = document.createElement("a");
      a.href = url;
      a.download = `${laneId}.csv`;
      a.click();
    }); //window.location.href = response.url;
  });

const handlerGenerator = (laneId) => {
    let laneId_encoded =`${encodeURIComponent(`${laneId}`)}`
    return () => downloadLaneData(laneId, laneId_encoded);
};

export default handlerGenerator;
