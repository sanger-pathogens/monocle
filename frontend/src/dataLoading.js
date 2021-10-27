export function getInstitutionStatus(fetch) {
  return Promise.all([
    getInstitutions(fetch),
    getBatches(fetch),
    getSequencingStatus(fetch),
    getPipelineStatus(fetch)
  ])
    .then(([institutions, batches, sequencingStatus, pipelineStatus]) =>
      institutions && collateInstitutionStatus({
        institutions,
        batches,
        sequencingStatus,
        pipelineStatus
      }));
}

export function getProjectProgress(fetch) {
  return getProjectProgressData(fetch)
    .then((progress) => {
      const progressData = progress?.data;
      if (progressData) {
        return {
          dates: progressData.date,
          datasets: [{
            name: "received",
            values: progressData["samples received"]
          }, {
            name: "sequenced",
            values: progressData["samples sequenced"]
          }]
        };
      }
    });
}

//TODO use service workers to cache response
export function getBatches(fetch) {
  return fetchDashboardResource("get_batches", "batches", fetch);
}

export function getUserDetails(fetch) {
  return fetchDashboardResource(
    "get_user_details", "user_details", fetch);
}

function getProjectProgressData(fetch) {
  return fetchDashboardResource(
    "get_progress", "progress_graph", fetch);
}

function getInstitutions(fetch) {
  return fetchDashboardResource(
    "get_institutions", "institutions", fetch);
}

function getSequencingStatus(fetch) {
  return fetchDashboardResource(
    "sequencing_status_summary", "sequencing_status", fetch);
}

function getPipelineStatus(fetch) {
  return fetchDashboardResource(
    "pipeline_status_summary", "pipeline_status", fetch);
}

function fetchDashboardResource(endpoint, resourceKey, fetch) {
  return fetch(`/dashboard-api/${endpoint}`)
    .then((response) =>
      response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
    .then((payload) => payload?.[resourceKey])
    .catch((err) => {
      console.log(
        `Error while fetching resource w/ key "${resourceKey}" from endpoint ${endpoint}: ${err}`
      );
      return Promise.reject(err);
    });
}

function collateInstitutionStatus({
  institutions,
  batches,
  sequencingStatus,
  pipelineStatus
}) {
  return Object.keys(institutions)
    .map((institutionKey) => ({
      name: institutions[institutionKey].name,
      batches: batches[institutionKey],
      sequencingStatus: sequencingStatus[institutionKey],
      pipelineStatus: {
        sequencedSuccess: sequencingStatus[institutionKey].success,
        ...pipelineStatus[institutionKey]
      },
      key: institutionKey
    }))
}
