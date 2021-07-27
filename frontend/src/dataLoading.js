export const MONOCLE_URL = "http://monocle.dev.pam.sanger.ac.uk";

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
            name: "samples received",
            values: progressData["samples received"]
          }, {
            name: "samples sequenced",
            values: progressData["samples sequenced"]
          }]
        };
      }
    });
}

export function getUserRole(fetch) {
  return fetchDashboardResource("get_user_details", "user_details", fetch)
    .then((userDetails) => userDetails?.type);
}

function getProjectProgressData(fetch) {
  return fetchDashboardResource(
    "get_progress", "progress_graph", fetch);
}

function getInstitutions(fetch) {
  return fetchDashboardResource(
    "get_institutions", "institutions", fetch);
}

function getBatches(fetch) {
  return fetchDashboardResource("get_batches", "batches", fetch);
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
  return fetch(`${MONOCLE_URL}/dashboard-api/${endpoint}`)
    .then((response) =>
      response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
    .then((payload) => payload?.[resourceKey])
    .catch((err) => (
      console.log(
        `Error while fetching resource w/ key "${resourceKey}" from endpoint ${endpoint}: ${err}`
      )
    ));
}

function collateInstitutionStatus({
  institutions,
  batches,
  sequencingStatus,
  pipelineStatus
}) {
  return Object.keys(institutions)
    .map((key) => ({
      name: institutions[key].name,
      batches: batches[key],
      sequencingStatus: sequencingStatus[key],
      pipelineStatus: {
        sequencedSuccess: sequencingStatus[key].success,
        ...pipelineStatus[key]
      },
      key
    }))
}
