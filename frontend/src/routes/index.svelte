<script>
	import { onMount } from "svelte";
	import { getInstitutionStatus, getProjectProgress } from "../dataLoading.js";
  import InstitutionStatus from './_dashboard/_InstitutionStatus.svelte';
  import LineChart from '$lib/components/LineChart.svelte';
	import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import MetadataUploadLink from './_dashboard/_MetadataUploadLink.svelte';

	let dashboardDataPromise = Promise.resolve();

	onMount(() => {
		dashboardDataPromise = Promise.all([
			getInstitutionStatus(fetch),
			getProjectProgress(fetch)
		]);
	});
</script>


{#await dashboardDataPromise}
	<LoadingIndicator midscreen={true} />

{:then [institutions = [], projectProgress = {}]}
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

{:catch error}
	<p>An unexpected error during page loading occured. Please try to reload the page.</p>

{/await}


<style>
p {
	text-align: center;
}
</style>

