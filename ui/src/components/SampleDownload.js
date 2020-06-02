const getLaneUrl = (laneId) => {
  let laneId_encoded =`${encodeURIComponent(`${laneId}`)}`
  let lane_url=`${window.env.DOWNLOAD_ROOT_URL}${laneId_encoded}`
  return lane_url
}

export default getLaneUrl;
