import { browser } from "$app/env";
import {
  DATA_TYPES,
  HTTP_HEADER_CONTENT_TYPE,
  HTTP_HEADERS_JSON,
  HTTP_POST,
  HTTP_STATUS_CODE_UNAUTHORIZED,
  MIME_TYPE_HTML,
  PATHNAME_LOGIN,
} from "$lib/constants.js";

const DASHBOARD_API_ENDPOINT = "/dashboard-api";
const EMPTY_STRING = "";
const FETCH_ERROR_PATTER_NOT_FOUND = "404 ";
const FETCH_ERROR_UNKNOWN = "unknown error";
const RE_HTML = /^\s*<!DOCTYPE/gi;

export function getInstitutionStatus(fetch) {
  return Promise.all([
    getInstitutions(fetch),
    getBatches(fetch),
    getSequencingStatus(fetch),
    getPipelineStatus(fetch),
  ]).then(
    ([institutions, batches, sequencingStatus, pipelineStatus]) =>
      institutions &&
      collateInstitutionStatus({
        institutions,
        batches,
        sequencingStatus,
        pipelineStatus,
      })
  );
}

export function getProjectProgress(fetch) {
  return getProjectProgressData(fetch).then((progress) => {
    const progressData = progress?.data;
    if (progressData) {
      return {
        dates: progressData.date,
        datasets: [
          {
            name: "received",
            values: progressData["samples received"],
          },
          {
            name: "sequenced",
            values: progressData["samples sequenced"],
          },
        ],
      };
    }
  });
}

//TODO use service workers to cache response
export function getBatches(fetch) {
  return fetchDashboardApiResource("get_batches", "batches", fetch);
}

export function getBulkDownloadInfo(params, fetch) {
  return fetchDashboardApiResource("bulk_download_info", null, fetch, {
    method: HTTP_POST,
    headers: HTTP_HEADERS_JSON,
    body: JSON.stringify(prepareBulkDownloadPayload(params)),
  });
}

export function getBulkDownloadUrls(params, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_urls",
    "download_urls",
    fetch,
    {
      method: HTTP_POST,
      headers: HTTP_HEADERS_JSON,
      body: JSON.stringify(prepareBulkDownloadPayload(params)),
    }
  );
}

export function getColumns(fetch) {
  return fetchDashboardApiResource(
    "get_field_attributes",
    "field_attributes",
    fetch
  );
}

export function getDistinctColumnValues(
  { instKeyBatchDatePairs, columns, filter },
  fetch
) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs),
    },
  };
  payload.fields = columns.reduce(
    (accum, column) => {
      const { fields, dataTypeToFieldsIndex } = accum;
      let fieldsIndex = dataTypeToFieldsIndex[column.dataType];
      if (fieldsIndex === undefined) {
        fieldsIndex = fields.length;
        dataTypeToFieldsIndex[column.dataType] = fieldsIndex;
        fields.push({ "field type": column.dataType, "field names": [] });
      }
      fields[fieldsIndex]["field names"].push(column.name);
      return accum;
    },
    { fields: [], dataTypeToFieldsIndex: {} }
  ).fields;

  addFiltersToPayload({ ...filter, payload });

  return fetchDashboardApiResource(
    "get_distinct_values",
    "distinct values",
    fetch,
    {
      method: HTTP_POST,
      headers: HTTP_HEADERS_JSON,
      body: JSON.stringify(payload),
    }
  );
}

export function getInstitutions(fetch) {
  return fetchDashboardApiResource("get_institutions", "institutions", fetch);
}

export function getSampleMetadata(
  { instKeyBatchDatePairs, filter, columns, numRows, startRow, asCsv },
  fetch
) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs),
    },
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
      headers: HTTP_HEADERS_JSON,
      body: JSON.stringify(payload),
    })
      .then((response) =>
        response.ok
          ? response.blob()
          : Promise.reject(`${response.status} ${response.statusText}`)
      )
      .catch((err) => handleFetchError(err, "get_metadata"));
  } else {
    addColumnsToPayload(columns, payload);
  }

  return fetchDashboardApiResource("get_metadata", null, fetch, {
    method: HTTP_POST,
    headers: HTTP_HEADERS_JSON,
    body: JSON.stringify(payload),
  });
}

export function getUserDetails(fetch) {
  return fetchDashboardApiResource("get_user_details", "user_details", fetch);
}

function getProjectProgressData(fetch) {
  return fetchDashboardApiResource("get_progress", "progress_graph", fetch);
}

function getSequencingStatus(fetch) {
  return fetchDashboardApiResource(
    "sequencing_status_summary",
    "sequencing_status",
    fetch
  );
}

function getPipelineStatus(fetch) {
  return fetchDashboardApiResource(
    "pipeline_status_summary",
    "pipeline_status",
    fetch
  );
}

export function getProjectInformation(fetch) {
  return fetchDashboardApiResource("interface", "project", fetch);
}

function fetchDashboardApiResource(endpoint, resourceKey, fetch, fetchOptions) {
  if (browser) {
    // Prevent API requests from the login page:
    if (location.pathname.endsWith(PATHNAME_LOGIN)) {
      return Promise.resolve({});
    }
  }
  return (
    fetchOptions
      ? fetch(`${DASHBOARD_API_ENDPOINT}/${endpoint}`, fetchOptions)
      : fetch(`${DASHBOARD_API_ENDPOINT}/${endpoint}`)
  )
    .then(async (response) => {
      const authenticated = await isProbablyAuthenticated(response);
      if (!authenticated && browser) {
        location.href = PATHNAME_LOGIN;
        return {};
      }
      return response.ok
        ? response.json()
        : Promise.reject(`${response.status} ${response.statusText}`);
    })
    .then((payload) => (resourceKey ? payload?.[resourceKey] : payload))
    .catch((err) => handleFetchError(err, endpoint, resourceKey));
}

function handleFetchError(err = FETCH_ERROR_UNKNOWN, endpoint, resourceKey) {
  if (err.startsWith?.(FETCH_ERROR_PATTER_NOT_FOUND)) {
    return Promise.resolve();
  }
  console.error(
    resourceKey
      ? `Error while fetching resource w/ key "${resourceKey}" from endpoint ${endpoint}: ${err}`
      : `Error while fetching resource from endpoint ${endpoint}: ${err}`
  );
  return Promise.reject(err);
}

function isProbablyAuthenticated(responseParam) {
  const contentTypeHeader =
    responseParam.headers.get(HTTP_HEADER_CONTENT_TYPE) || EMPTY_STRING;
  // An HTML response indicates that the request was redirected to the login page, ie it's not authenticated.
  if (
    contentTypeHeader.includes(MIME_TYPE_HTML) ||
    responseParam.status === HTTP_STATUS_CODE_UNAUTHORIZED
  ) {
    return Promise.resolve(false);
  }
  // Any other non-empty content type indicates that the user is authenticated:
  if (contentTypeHeader.length) {
    return Promise.resolve(true);
  }
  // Cloning a response is necessary because the reponse body can be read only once. (So if we subsequently re-read it, there will be an exception.)
  const response = responseParam.clone();
  // An empty response body (w/ an empty content type HTTP header from above) mean that the response is a cached
  // response w/ the login page HTML, ie the user is not authenticated:
  return response
    .text()
    .then((responseBody) => responseBody && !RE_HTML.test(responseBody));
}

function collateInstitutionStatus({
  institutions,
  batches,
  sequencingStatus,
  pipelineStatus,
}) {
  return Object.keys(institutions).map((institutionKey) => ({
    name: institutions[institutionKey].name,
    batches: batches[institutionKey],
    sequencingStatus: sequencingStatus[institutionKey],
    pipelineStatus: {
      sequencedSuccess: sequencingStatus[institutionKey].success,
      ...pipelineStatus[institutionKey],
    },
    key: institutionKey,
  }));
}

function prepareBulkDownloadPayload({
  instKeyBatchDatePairs,
  filter,
  assemblies,
  annotations,
  reads,
  maxSamplesPerZip,
}) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs),
    },
    assemblies,
    annotations,
    reads,
  };
  if (maxSamplesPerZip) {
    payload["max samples per zip"] = maxSamplesPerZip;
  }

  addFiltersToPayload({ ...filter, payload });

  return payload;
}

function addColumnsToPayload(columns = {}, payload) {
  DATA_TYPES.forEach((dataType) => {
    if (columns[dataType]?.length) {
      payload[`${dataType} columns`] = columns[dataType];
    } else {
      payload[dataType] = false;
    }
  });
}

function addFiltersToPayload({
  filterState = {},
  payload,
  distinctColumnValuesState,
}) {
  DATA_TYPES.forEach((dataType) => {
    const filterStateForDataType = filterState[dataType] || {};
    const columnNames = Object.keys(filterStateForDataType);
    if (columnNames.length) {
      const payloadFilter = {};
      columnNames.forEach((columnName) => {
        if (filterStateForDataType[columnName].exclude) {
          const valuesToExclude = new Set(
            filterStateForDataType[columnName].values
          );
          payloadFilter[columnName] = distinctColumnValuesState[dataType][
            columnName
          ].filter((columnValue) => !valuesToExclude.has(columnValue));
        } else {
          payloadFilter[columnName] = filterStateForDataType[columnName].values;
        }
      });
      payload["sample filters"][dataType] = payloadFilter;
    }
  });
}

export function transformInstKeyBatchDatePairsIntoPayload(
  instKeyBatchDatePairs = []
) {
  return instKeyBatchDatePairs.map(([instKey, batchDate]) => ({
    "institution key": instKey,
    "batch date": batchDate,
  }));
}
