import { MONOCLE_URL } from "./dataLoading.js";

const LOCAL_URL = "http://dash-api/dashboard-api/";
const DASHBOARD_API_URL = `${MONOCLE_URL}/dashboard-api/`;
// This function allows us to modify a fetch request that happens in the `load` function
// for the server. See more: // https://kit.svelte.dev/docs#hooks-serverfetch
export async function serverFetch(request) {
	const isDashboardAPI = request.url.startsWith(DASHBOARD_API_URL);
	return fetch(isDashboardAPI ?
		cloneRequestWithNewURL(request, DASHBOARD_API_URL, LOCAL_URL)
		: request
	);
}

function cloneRequestWithNewURL(request, originalURL, newURL) {
	return new Request(
		request.url.replace(originalURL, newURL),
		request
	);
}
