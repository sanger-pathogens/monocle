/*
 * Runtime settings
 *
 * Because we transpile the React app at Docker image build time,
 * it's not possible to easily pass environment variables for
 * configuration at container runtime, since we only have static
 * files to be served.
 *
 * This file follows the dynamic approach described at:
 *   https://levelup.gitconnected.com/handling-multiple-environments-in-react-with-docker-543762989783
 *
 * To overwrite the settings at container runtime, simply mount
 * a new settings.js file to eg. /usr/share/nginx/html
 */
window.env = {
  GRAPHQL_API_URL: "http://localhost:8000/graphql/",
  DOWNLOAD_ROOT_URL: "http://localhost:8000/",
};

