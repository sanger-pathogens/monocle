<script context="module">
	import { getInstitutionStatus, getProjectProgress } from "../dataLoading.js";

	// This function loads the data expected by the component, before the component is created.
	// It can run both during server-side rendering and in the client. See https://kit.svelte.dev/docs#loading.
	export async function load({ fetch }) {
		const [institutions, projectProgress] = await Promise.all([
			getInstitutionStatus(fetch),
			getProjectProgress(fetch)
		]);

		return {
			props: {
				institutions,
				projectProgress
			}
		};
	}
</script>

<script>
  import InstitutionStatus from './_dashboard/_InstitutionStatus.svelte';
  import LineChart from '$lib/components/LineChart.svelte';
  import MetadataUploadLink from './_dashboard/_MetadataUploadLink.svelte';

  export let institutions = [];
  export let projectProgress = {};
</script>


<MetadataUploadLink />

<LineChart
	title="Project Progress"
  datasets={projectProgress.datasets}
  labels={projectProgress.dates}
/>

{#each institutions as { name, batches, sequencingStatus, pipelineStatus, key } (key)}
	<InstitutionStatus
		{batches}
		{sequencingStatus}
		{pipelineStatus}
		institutionName={name}
	/>
{:else}
	<p>No institutions found for this account. This may be an error, so please try to reload the page or to log out and log in again.</p>
{/each}


<style>
p {
	text-align: center;
}
</style>

