<script>
  import { onMount } from "svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import BatchSelector from "./_BatchSelector.svelte";
  import { getBatches, getBulkDownloadInfo, getBulkDownloadUrls, getInstitutions } from "../../../dataLoading.js";

  const MAX_REQUEST_FREQUENCY_MS = 1500;
  const PAGE_TITLE_ID = "bulk-download-title";
  const PROMISE_STATUS_REJECTED = "rejected";

  let formValues = {
    annotations: true,
    assemblies: true
  };
  let dataPromise = Promise.resolve();
  let debounceTimeoutId;
  let downloadEstimate = {};
  let downloadLinksRequested;
  let downloadLink;
  let selectedBatches = null;

  $: formComplete = selectedBatches?.length &&
      (formValues.annotations || formValues.assemblies);

  // These arguments are passed just to indicate to Svelte that this reactive statement
  // should re-run only when one of the args has changed.
  $: updateDownloadEstimate(selectedBatches, formValues);

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

  function updateDownloadEstimate() {
    unsetDownloadEstimate();
    debounce(_updateDownloadEstimate);
  }

  function _updateDownloadEstimate() {
    if (!formComplete) {
      return;
    }

    getBulkDownloadInfo(
      selectedBatches.map(({value}) => value),
      formValues,
      fetch
    )
      .then(({size, size_zipped}) => {
        // Commented out because BE currently doesn't compress for performace reasons:
        // downloadEstimate.size = size;
        downloadEstimate.sizeZipped = size_zipped;
      })
      .catch(unsetDownloadEstimate);
  }

  function unsetDownloadEstimate() {
    downloadEstimate = {};
  }

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

  function onSubmit() {
    if (!formComplete) {
      // Prevents submitting the form on Enter while the confirm btn is disabled.
      return;
    }

    downloadLinksRequested =
      confirm("You won't be able to change the parameters if you proceed.");
    if (downloadLinksRequested) {
      const selectedBatchValues = selectedBatches?.map(({value}) => value);
      getBulkDownloadUrls(selectedBatchValues, formValues, fetch)
        .then((downloadLinks = []) => {
          downloadLink = downloadLinks[0];
          if (!downloadLink) {
            console.error("The list of download URLs returned from the server is empty.");
            return Promise.reject();
          }
        })
        .catch(() => {
          downloadLinksRequested = false;
          alert("Error while generating a download link. Please try again.");
        });
    }
  }

  function debounce(callback) {
    // Clear the previous timeout and set a new one.
    clearTimeout(debounceTimeoutId);
    debounceTimeoutId = setTimeout(callback, MAX_REQUEST_FREQUENCY_MS);
  }
</script>


<h2 id={PAGE_TITLE_ID}>Sample bulk download</h2>

{#await dataPromise}
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
        <legend>Split download (coming soon)</legend>
        <select>
          {#if downloadEstimate?.sizeZipped}
            <option selected>
              1 download of {downloadEstimate.sizeZipped}
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

  {#if downloadLinksRequested}
    {#if downloadLink}
      <!-- Leading `/` in `href` is needed to make the download path relative to the root URL. -->
      <a
        href={`/${downloadLink}`}
        target="_blank"
        class="download-link"
        download
      >
        Download samples
      </a>
    {:else}
      <LoadingIndicator
        message="Please wait: generating a file archive can take several minutes if thousands of samples are involved."
      />
    {/if}
  {/if}
{:catch error}
    <p>An unexpected error occured during page loading. Please try again by reloading the page.</p>

{/await}


<style>
form {
  width: var(--width-reading);
  max-width: 100%;
}

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

