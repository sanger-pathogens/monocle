const DASHBOARD_API_ENDPOINT = "/dashboard-api";
const DATA_TYPES = ["metadata", "in silico"];
const FETCH_ERROR_PATTER_NOT_FOUND = "404 ";
const FETCH_ERROR_UNKNOWN = "unknown error";
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

export function getBulkDownloadInfo(params, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_info", null, fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(prepareBulkDownloadPayload(params))
    });
}

export function getBulkDownloadUrls(params, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_urls", "download_urls", fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(prepareBulkDownloadPayload(params))
    });
}

export function getDistinctColumnValues({ instKeyBatchDatePairs, columns, filter }, fetch) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
    }
  };
  payload.fields = columns.reduce((accum, column) => {
      const { fields, dataTypeToFieldsIndex } = accum;
      let fieldsIndex = dataTypeToFieldsIndex[column.dataType];
      if (fieldsIndex === undefined) {
        fieldsIndex = fields.length;
        dataTypeToFieldsIndex[column.dataType] = fieldsIndex;
        fields.push({ "field type": column.dataType, "field names": [] });
      }
      fields[fieldsIndex]["field names"].push(column.name);
      return accum;
    }, { fields: [], dataTypeToFieldsIndex: {} }
  ).fields;

  addFiltersToPayload({ ...filter, payload });

  return fetchDashboardApiResource("get_distinct_values", "distinct values", fetch, {
    method: HTTP_POST,
    headers: JSON_HEADERS,
    body: JSON.stringify(payload)
  });
}

export function getInstitutions(fetch) {
  return fetchDashboardApiResource(
    "get_institutions", "institutions", fetch);
}

export function getSampleMetadata({
  instKeyBatchDatePairs,
  filter,
  numRows,
  startRow,
  asCsv
},
fetch
) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
    }
  };

  addFiltersToPayload({ ...filter, payload });

  if (Number.isInteger(numRows)) {
    payload["num rows"] = numRows;
  }
  if (Number.isInteger(startRow)) {
    payload["start row"] = startRow;
  }

  if (asCsv === true) {
    payload["as csv"] = true;
    return fetch(`${DASHBOARD_API_ENDPOINT}/get_metadata`, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(payload)
    })
      .then((response) =>
        response.ok ? response.blob() : Promise.reject(`${response.status} ${response.statusText}`))
      .catch((err) =>
        handleFetchError(err, "get_metadata"));
  }
  else {
    payload["in silico"] = false;
    payload["qc data"] = false;
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
    fetch(`${DASHBOARD_API_ENDPOINT}/${endpoint}`, fetchOptions) :
    fetch(`${DASHBOARD_API_ENDPOINT}/${endpoint}`)
  )
    .then((response) =>
      response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
    .then((payload) => resourceKey ? payload?.[resourceKey] : payload)
    .catch((err) => handleFetchError(err, endpoint, resourceKey));
}

function handleFetchError(err = FETCH_ERROR_UNKNOWN, endpoint, resourceKey) {
  if (err.startsWith?.(FETCH_ERROR_PATTER_NOT_FOUND)) {
    return Promise.resolve();
  }
  console.error(resourceKey ?
    `Error while fetching resource w/ key "${resourceKey}" from endpoint ${endpoint}: ${err}` :
    `Error while fetching resource from endpoint ${endpoint}: ${err}`
  );
  return Promise.reject(err);
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

function prepareBulkDownloadPayload({
  instKeyBatchDatePairs,
  filter,
  assemblies,
  annotations
}) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
    },
    assemblies,
    annotations
  };

  addFiltersToPayload({ ...filter, payload });

  return payload;
}

function addFiltersToPayload({ filterState = {}, payload, distinctColumnValues }) {
  DATA_TYPES.forEach((dataType) => {
    const filterStateForDataType = filterState[dataType] || {};
    const columnNames = Object.keys(filterStateForDataType);
    if (columnNames.length) {
      const payloadFilter = {};
      columnNames.forEach((columnName) => {
        if (filterStateForDataType[columnName].exclude) {
          const valuesToExclude = new Set(filterStateForDataType[columnName].values);
          payloadFilter[columnName] = distinctColumnValues[dataType][columnName].filter((columnValue) =>
            !valuesToExclude.has(columnValue));
        }
        else {
          payloadFilter[columnName] = filterStateForDataType[columnName].values;
        }
      });
      payload["sample filters"][dataType] = payloadFilter;
    }
  });
}

export function transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs = []) {
  return instKeyBatchDatePairs.map(([instKey, batchDate]) => (
    { "institution key": instKey, "batch date": batchDate }
  ));
}
