const DASHBOARD_API_INTERNAL_URL = "http://dash-api:5000/dashboard-api";
const MONOCLE_URL = "http://monocle.pam.sanger.ac.uk";
const DASHBOARD_API_URL = `${MONOCLE_URL}/dashboard-api`;
const OPTIONS_RESOLVE = Object.freeze({ ssr: false });


// FIXME add unit test
export async function handle({ event, resolve }) {
  return resolve(event, OPTIONS_RESOLVE);
}


// This function allows us to modify a fetch request that happens in the `load` function
// for the server. See more: // https://kit.svelte.dev/docs#hooks-serverfetch
//FIXME: update SvelteKit & rename `serverFetch` to `externalFetch` (https://kit.svelte.dev/docs#hooks-externalfetch)
export async function serverFetch(request) {
  const isDashboardAPI = request.url.startsWith(DASHBOARD_API_URL);
  return fetch(isDashboardAPI ?
    cloneRequestWithNewURL(request, DASHBOARD_API_URL, DASHBOARD_API_INTERNAL_URL)
    : request
  );
}

function cloneRequestWithNewURL(request, originalURL, newURL) {
  return new Request(
    request.url.replace(originalURL, newURL),
    request
  );
}
