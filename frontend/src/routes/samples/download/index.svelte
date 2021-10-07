<script>
  import { onMount } from "svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import BatchSelector from "./_BatchSelector.svelte";
  import { getBatches, getBulkDownloadInfo, getBulkDownloadUrls } from "../../../dataLoading.js";

  const PAGE_TITLE_ID = "bulk-download-title";

  let formValues = {
    annotations: true,
    assemblies: true
  };
  let batchesPromise = Promise.resolve();
  let downloadEstimate = {};
  let downloadLinksRequested;
  let downloadLink;
  let selectedBatches = null;

  $: formComplete = selectedBatches &&
      (formValues.annotations || formValues.assemblies);

  // These arguments are passed just to indicate to Svelte that this reactive statement
  // should re-run only when one of the args has changed.
  $: updateDownloadEstimate(selectedBatches, formValues);

  onMount(() => {
    batchesPromise = getBatches(fetch)
      .then((batches) => makeListOfBatches(batches));
  });

  // FIXME: debounce to avoid hammering the endpoint w/ requests
  function updateDownloadEstimate() {
    if (!formComplete) {
      unsetDownloadEstimate();
      return;
    }

    getBulkDownloadInfo(
      selectedBatches.map(({value}) => value),
      formValues,
      fetch
    )
      .then(({size, size_zipped}) => {
        downloadEstimate.size = size;
        downloadEstimate.sizeZipped = size_zipped;
      })
      .catch(unsetDownloadEstimate);
  }

  function unsetDownloadEstimate() {
    downloadEstimate = {};
  }

  function makeListOfBatches(batches = {}) {
    return Object.keys(batches)
      .map((institutionKey) =>
        batches[institutionKey].deliveries.map((batch) =>
          makeBatchListItem(batch, institutionKey)))
      .flat();
  }

  function makeBatchListItem({ name, date, number: numSamples }, institutionKey) {
    const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
    return {
      label: `${date}: ${name}${numSamplesText}`,
      value: date,
      group: institutionKey
    };
  }

  function onSubmit() {
    if (!formComplete) {
      // Prevents submitting the form on Enter while the confirm btn is disabled.
      return;
    }

    downloadLinksRequested =
      confirm("You won't be able to change the parameters if you proceed.");
    if (downloadLinksRequested) {
      const batchDates = selectedBatches?.map(({value}) => value);
      getBulkDownloadUrls(batchDates, formValues, fetch)
        .then((downloadLinks = []) => {
          downloadLink = downloadLinks[0];
          if (!downloadLink) {
            console.error("The list of download URLs returned from the server is empty.");
            return Promise.reject();
          }
        })
        .catch(() => {
          downloadLinksRequested = false;
          alert(`Error while generating a download link. Please try again.`);
        });
    }
  }
</script>


<h2 id={PAGE_TITLE_ID}>Sample bulk download</h2>

{#await batchesPromise}
  <LoadingIndicator />

{:then batchList}
  <form
    aria-labelledby={PAGE_TITLE_ID}
    on:submit|preventDefault={onSubmit}
  >
    <fieldset
      disabled={downloadLinksRequested}
      class:disabled={downloadLinksRequested}
    >

      <fieldset class="batch-selection-section">
        <legend>Select batches to download</legend>
        <BatchSelector
          bind:selectedBatches
          {batchList}
        />
      </fieldset>

      <fieldset class="data-type-section">
        <legend>Data type</legend>

        <label>
          <input
            type="checkbox"
            bind:checked={formValues.assemblies}
          />
          Assemblies
        </label>

        <label>
          <input
            type="checkbox"
            bind:checked={formValues.annotations}
          />
          Annotations
        </label>

        <!-- To be done in a future version of Monocle.
        <label class="disabled">
          <input type="checkbox" />
          Reads ( ⚠️ may increase the size drastically)
        </label>
        -->
      </fieldset>

      <fieldset disabled={true}>
        <legend>Download size</legend>
        <select>
          {#if downloadEstimate?.size}
            <option selected>
              1 download of {downloadEstimate.sizeZipped} ({downloadEstimate.size} unzipped)
            </option>
          {/if}
        </select>
      </fieldset>

      <button
        type="submit"
        class="primary"
        disabled={!formComplete}
      >
        Confirm
      </button>

    </fieldset>
  </form>

  {#if downloadLink}
    <a
      href={downloadLink}
      target="_blank"
      class="download-link"
      download
    >
      Download samples
    </a>
  {/if}
{:catch error}
    <p>An unexpected error occured during page loading. Please try again by reloading the page.</p>

{/await}


<style>
form > fieldset {
  padding: 0;
}

button[type=submit] {
  display: block;
  margin-top: 2.5rem;
  margin-left: .9rem;
}

select {
  min-width: 12rem;
  max-width: 90%;
}

.batch-selection-section {
  align-items: flex-start;
  margin-bottom: 1rem;
}
@media (min-width: 480px) {
  .batch-selection-section {
    display: flex;
  }
}

.data-type-section {
  display: flex;
  flex-direction: column;
  /* This prevents the checkbox labels from being clickable across all of the container's width. */
  align-items: flex-start;
}

.download-link {
  display: inline-block;
  margin: 2rem 0;
}
</style>

