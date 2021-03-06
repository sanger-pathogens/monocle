const baseUrl = `${document.URL.startsWith("https") ? "https" : "http"}://${document.domain}/api/`;

window.env = {
  API_ROOT_URL: baseUrl,
  GRAPHQL_API_URL: `${baseUrl}graphql/`,
  DOWNLOAD_ROOT_URL: `${baseUrl}SampleDownload/`,
  USE_AUTHENTICATION: true,
};
