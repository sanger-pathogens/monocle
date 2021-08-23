import { MONOCLE_URL } from "./dataLoading.js";

const DASHBOARD_API_INTERNAL_URL = "http://dash-api:5000/dashboard-api";
const DASHBOARD_API_URL = `${MONOCLE_URL}/dashboard-api`;

export async function getSession() {
	const userRole = await fetch(`${DASHBOARD_API_URL}/get_user_details`)
		.then((response) =>
			response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
		.then(({ user_details } = {}) => user_details?.type)
		.catch((err) => (
			console.log(`Error while fetching user details: ${err}`)
		));

	return {
		user: {
			role: userRole
		}
	};
}

// This function allows us to modify a fetch request that happens in the `load` function
// for the server. See more: // https://kit.svelte.dev/docs#hooks-serverfetch
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
