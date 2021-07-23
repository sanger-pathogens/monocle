<script context="module">
	// This function loads the data expected by the component, before the component is created.
	// It can run both during server-side rendering and in the client. See https://kit.svelte.dev/docs#loading.
	export async function load({ fetch }) {
		const { institution_status: institutionStatus, progress_graph: projectProgress } =
			await fetch("/legacy_dashboard/data/summary/")
				.then((response) => response.json());

		return {
			props: {
				institutions: collateInstitutionStatus(institutionStatus),
				projectProgress: {
					dates: projectProgress.data.date,
					datasets: [{
						name: "samples received",
						values: projectProgress.data["samples received"]
					}, {
						name: "samples sequenced",
						values: projectProgress.data["samples sequenced"]
					}]
				}
			}
		};
	}

	function collateInstitutionStatus({
		institutions,
		batches,
		sequencing_status,
		pipeline_status
	}) {
		return Object.keys(institutions)
			.map((key) => ({
				name: institutions[key].name,
				batches: batches[key],
				sequencingStatus: sequencing_status[key],
				pipelineStatus: {
					sequencedSuccess: sequencing_status[key].success,
					...pipeline_status[key]
				},
				key
			}))
	}
</script>

<script>
  import InstitutionStatus from './_dashboard/_InstitutionStatus.svelte';
  import LineChart from '$lib/components/LineChart.svelte';
  import MetadataUploadLink from './_dashboard/_MetadataUploadLink.svelte';

  export let institutions;
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
