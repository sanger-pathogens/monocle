<script>
  import { onMount } from "svelte";
  import { session as appSession } from "$app/stores";
  import {
    getInstitutionStatus,
    getProjectProgress,
  } from "$lib/dataLoading.js";
  import DataUploadLinks from "./_dashboard/_DataUploadLinks.svelte";
  import InstitutionStatus from "./_dashboard/_InstitutionStatus.svelte";
  import LineChart from "$lib/components/LineChart.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import SampleDataLink from "./_dashboard/_SampleDataLink.svelte";

  export let session = appSession;

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
  <nav>
    <SampleDataLink />
    <DataUploadLinks {session} />
  </nav>

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

  nav {
    display: flex;
    flex-direction: column;
    align-self: flex-end;
    margin-right: -1rem;

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

  article {
    max-width: 100%;
  }
</style>
