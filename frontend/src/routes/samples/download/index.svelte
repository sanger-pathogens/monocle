<script>
  import { onMount } from "svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import BatchSelector from "./_BatchSelector.svelte";
  import BulkDownload from "./_BulkDownload.svelte";
  import SampleMetadataViewer from "./_metadata_viewer/_SampleMetadataViewer.svelte";
  import {
    getBatches,
    getInstitutions
  } from "$lib/dataLoading.js";

  const PROMISE_STATUS_REJECTED = "rejected";

  // FIXME: try unresolved promise
  let dataPromise = Promise.resolve();
  let selectedBatches = null;

  $: selectedInstKeyBatchDatePairs = selectedBatches?.map(({value}) => value);

  onMount(() => {
    dataPromise = Promise.allSettled([ getBatches(fetch), getInstitutions(fetch) ])
      .then(([batchesSettledPromise, institutionsSettledPromise]) => {
        if (batchesSettledPromise.status === PROMISE_STATUS_REJECTED) {
          console.error(`/get_batches rejected: ${batchesSettledPromise.reason}`);
          return Promise.reject(batchesSettledPromise.reason);
        }
        return makeListOfBatches(batchesSettledPromise.value, institutionsSettledPromise.value);
      })
      .catch((err) => {
        console.error(`Error while fetching batches and institutions: ${err}`);
        return Promise.reject(err);
      });
  });

  function makeListOfBatches(batches = {}, institutions = {}) {
    return Object.keys(batches)
      .reduce(((accumListOfBatches, institutionKey) =>
        addBatchListItems(
          accumListOfBatches,
          batches[institutionKey].deliveries,
          institutionKey,
          institutions[institutionKey]?.name
        )
      ), []);
  }

  function addBatchListItems(accumListOfBatches, batches = [], institutionKey, institutionName) {
    return batches.reduce((thisAccumListOfBatches, batch) => {
      thisAccumListOfBatches.push(makeBatchListItem(batch, institutionKey, institutionName));
      return thisAccumListOfBatches;
    }, accumListOfBatches);
  }

  function makeBatchListItem({ name, date, number: numSamples }, institutionKey, institutionName) {
    const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
    return {
      label: `${date}: ${name}${numSamplesText}`,
      value: [institutionKey, date],
      group: institutionName || institutionKey
    };
  }
</script>


<h2>Sample data viewer</h2>

{#await dataPromise}
  <LoadingIndicator />

{:then batchList}
  <section class="batch-selection-section">
    <h3>Select batches</h3>
    <BatchSelector
      bind:selectedBatches
      {batchList}
    />
  </section>

  <SampleMetadataViewer batches={selectedInstKeyBatchDatePairs} />

  <!-- FIXME test -->
  <details>
    <summary id="sample-bulk-download-label">Download selected samples</summary>
    <BulkDownload
      ariaLabelledby="sample-bulk-download-label"
      batches={selectedInstKeyBatchDatePairs}
    />
  </details>

{:catch}
  <p>An unexpected error occured during page loading. Please try again by reloading the page.</p>

{/await}


<style>
.batch-selection-section {
  margin-bottom: 2rem;
  width: 100%;
}
</style>

