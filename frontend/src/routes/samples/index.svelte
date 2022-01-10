<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import DownloadIcon from "$lib/components/icons/DownloadIcon.svelte";
  import LoadingIcon from "$lib/components/icons/LoadingIcon.svelte";
  import BatchSelector from "./_BatchSelector.svelte";
  import BulkDownload from "./_BulkDownload.svelte";
  import SampleMetadataViewer from "./_metadata_viewer/_SampleMetadataViewer.svelte";
  import {
    getBatches,
    getInstitutions,
    getSampleMetadata
  } from "$lib/dataLoading.js";

  const PROMISE_STATUS_REJECTED = "rejected";

  export let injectedCreateAnchorElement = undefined;

  const dataPromise = Promise.allSettled([ getBatches(fetch), getInstitutions(fetch) ])
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
  let isPreparingMetadataDownload = false;
  let selectedBatches = null;

  $: selectedInstKeyBatchDatePairs = selectedBatches?.map(({value}) => value);

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

  function downloadMetadata() {
    if (!selectedBatches?.length) {
      return;
    }

    isPreparingMetadataDownload = true;

    let csvBlobUrl;
    let hiddenDownloadLink;
    getSampleMetadata({
      instKeyBatchDatePairs: selectedInstKeyBatchDatePairs,
      asCsv: true
    }, fetch)
    .then((csvBlob) => {
      csvBlobUrl = URL.createObjectURL(csvBlob);
      hiddenDownloadLink = document.body.appendChild(
        createHiddenDownloadLink(csvBlobUrl, "monocle-sample-metadata.csv"));
      hiddenDownloadLink.click();
    })
    .catch((err) => console.error(`Error on creating metadata download: ${err}`))
    .finally(() => {
      isPreparingMetadataDownload = false;
      hiddenDownloadLink && document.body.removeChild(hiddenDownloadLink);
      URL.revokeObjectURL(csvBlobUrl);
    });
  }

  function createHiddenDownloadLink(url, fileName) {
    const a = injectedCreateAnchorElement?.() || document.createElement("a");
    a.style = "display: none";
    a.href = url;
    a.download = fileName;
    return a;
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

  {#if selectedBatches?.length}
    <div class="download-btns">
      <button
        aria-label="Download samples (FIXME GB)"
        class="compact"
        type="button"
      >
        Samples (FIXME GB) <DownloadIcon />
      </button>

      <button
        aria-label={isPreparingMetadataDownload ? null : "Download metadata"}
        on:click={downloadMetadata}
        class="compact"
        type="button"
        disabled={isPreparingMetadataDownload}
      >
        {#if isPreparingMetadataDownload}
          Preparing download <LoadingIcon />
        {:else}
          Metadata <DownloadIcon />
        {/if}
      </button>
    </div>
  {/if}

  <SampleMetadataViewer batches={selectedInstKeyBatchDatePairs} />

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
  margin-bottom: 2.6rem;
  width: 100%;
}

.download-btns button {
  margin-right: 1rem;
}
</style>

