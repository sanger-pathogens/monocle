<script>
  import { onMount } from "svelte";
  import {
    getInstitutionStatus,
    getProjectProgress,
  } from "$lib/dataLoading.js";
  import LineChart from "$lib/components/LineChart.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import AppMenu from "./_app-menu/index.svelte";
  import InstitutionStatus from "./_dashboard/InstitutionStatus.svelte";

  let dashboardDataPromise = new Promise(() => {});

  onMount(() => {
    dashboardDataPromise = Promise.all([
      getInstitutionStatus(fetch),
      getProjectProgress(fetch),
    ]);
  });
</script>

{#await dashboardDataPromise}
  <LoadingIndicator midscreen={true} />
{:then [institutions = [], projectProgress = { }]}
  <AppMenu />

  <article>
    <h2>Project Progress</h2>
    <LineChart
      datasets={projectProgress.datasets}
      xLabels={projectProgress.dates}
      yLabel="# of samples"
    />
  </article>

  {#each institutions as { batches, sequencingStatus, pipelineStatus, name, key } (key)}
    <InstitutionStatus
      {batches}
      {sequencingStatus}
      {pipelineStatus}
      institutionKey={key}
      institutionName={name}
    />
  {:else}
    <p>
      No institutions found for this account. This may be an error, so please
      try to reload the page or to log out and log in again.
    </p>
  {/each}
{:catch}
  <p>
    An unexpected error occured during page loading. Please try again by
    reloading the page.
  </p>
{/await}

<style>
  p {
    text-align: center;
  }

  article {
    max-width: 100%;
  }
</style>
