<script>
  import { onMount } from "svelte";
  import { getInstitutionStatus, getProjectProgress } from "../dataLoading.js";
  import InstitutionStatus from "./_dashboard/_InstitutionStatus.svelte";
  import LineChart from "$lib/components/LineChart.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import InsilicoUploadLink from "./_dashboard/_InsilicoUploadLink.svelte";
  import MetadataUploadLink from "./_dashboard/_MetadataUploadLink.svelte";

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
  <nav>
    <MetadataUploadLink />
    <InsilicoUploadLink style="margin-top: .3rem" />
  </nav>

  <LineChart
    title="Project Progress"
    datasets={projectProgress.datasets}
    xLabels={projectProgress.dates}
    yLabel="# of samples"
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
  <p>An unexpected error occured during page loading. Please try again by reloading the page.</p>

{/await}


<style>
p {
  text-align: center;
}

nav {
  display: flex;
  flex-direction: column;
  align-self: flex-end;
  margin-right: -0.8rem;

  position: sticky;
  top: 1rem;
  z-index: 9;
}
@media (min-width: 2000px) {
  /* This pushes the menu w/ the upload buttoms further to the right for larger screens. */
  nav {
    margin-right: -8rem;
  }
}
</style>

