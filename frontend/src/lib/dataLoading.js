const HTTP_POST = "POST";
const JSON_HEADERS = { "Content-Type": "application/json" };

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
  return fetchDashboardApiResource("get_batches", "batches", fetch);
}

export function getBulkDownloadInfo(instKeyBatchDatePairs, { assemblies, annotations }, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_info", null, fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify({
        "sample filters": {
          batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
        },
        assemblies,
        annotations
      })
    });
}

export function getBulkDownloadUrls(instKeyBatchDatePairs, { assemblies, annotations }, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_urls", "download_urls", fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify({
        "sample filters": {
          batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
        },
        assemblies,
        annotations
      })
    });
}

export function getInstitutions(fetch) {
  return fetchDashboardApiResource(
    "get_institutions", "institutions", fetch);
}

export function getSampleMetadata({
  instKeyBatchDatePairs,
  numRows,
  startRow
},
fetch
) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
    }
  };
  if (Number.isInteger(numRows)) {
    payload["num rows"] = numRows;
  }
  if (Number.isInteger(startRow)) {
    payload["start row"] = startRow;
  }

  return fetchDashboardApiResource(
    "get_metadata", null, fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(payload)
    });
}

export function getUserDetails(fetch) {
  return fetchDashboardApiResource(
    "get_user_details", "user_details", fetch);
}

function getProjectProgressData(fetch) {
  return fetchDashboardApiResource(
    "get_progress", "progress_graph", fetch);
}

function getSequencingStatus(fetch) {
  return fetchDashboardApiResource(
    "sequencing_status_summary", "sequencing_status", fetch);
}

function getPipelineStatus(fetch) {
  return fetchDashboardApiResource(
    "pipeline_status_summary", "pipeline_status", fetch);
}

function fetchDashboardApiResource(endpoint, resourceKey, fetch, fetchOptions) {
  return (fetchOptions ?
    fetch(`/dashboard-api/${endpoint}`, fetchOptions) :
    fetch(`/dashboard-api/${endpoint}`)
  )
    .then((response) =>
      response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
    .then((payload) => resourceKey ? payload?.[resourceKey] : payload)
    .catch((err) => {
      console.error(resourceKey ?
        `Error while fetching resource w/ key "${resourceKey}" from endpoint ${endpoint}: ${err}` :
        `Error while fetching resource from endpoint ${endpoint}: ${err}`
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
    }));
}

function transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs = []) {
  return instKeyBatchDatePairs.map(([instKey, batchDate]) => (
    { "institution key": instKey, "batch date": batchDate }
  ));
}