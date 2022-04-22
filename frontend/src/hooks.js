const DASHBOARD_API_INTERNAL_URL = "http://dash-api:5000/dashboard-api";
const MONOCLE_URL = "http://monocle.pam.sanger.ac.uk";
const DASHBOARD_API_URL = `${MONOCLE_URL}/dashboard-api`;
const OPTIONS_RESOLVE = Object.freeze({ ssr: false });


export async function handle({ event, resolve }) {
  return resolve(event, OPTIONS_RESOLVE);
}


// This function allows us to modify a fetch request for an external resource that happens inside
// a `load` function that runs on the server (or during pre-rendering). See: https://kit.svelte.dev/docs/hooks#externalfetch.
// In this case, for SSR we want to hit the dashboard API directly, bypassing the load balancer.
export async function externalFetch(request) {
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
