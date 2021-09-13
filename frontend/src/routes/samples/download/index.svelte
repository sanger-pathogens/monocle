<script>
  import { onMount } from "svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import BatchSelector from "./_BatchSelector.svelte";
  import { getBatches } from "../../../dataLoading.js";

  let downloadLinksRequested;
  let downloadLink;
  let batchesPromise = Promise.resolve();
  let selectedBatches = null;

  onMount(() => {
    batchesPromise = getBatches(fetch)
      .then((batches) => makeListOfBatches(batches));
  });

  function makeListOfBatches(batches = {}) {
    return Object.keys(batches)
      .map((institutionKey) =>
        batches[institutionKey].deliveries.map((batch) =>
          makeBatchListItem(batch, institutionKey)))
      .flat();
  }

  function makeBatchListItem({ name, date, number: numSamples }, institutionKey) {
    const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
    const batchNameWithData = `${date}: ${name}${numSamplesText}`;
    return {
      label: batchNameWithData,
      value: batchNameWithData,
      group: institutionKey
    };
  }

  function onSubmit() {
    downloadLinksRequested =
      confirm("You won't be able to change the parameters if you proceed.");
    if (downloadLinksRequested) {
      fetchDownloadLinks()
        .then((downloadLinks = []) => {
          downloadLink = downloadLinks[0];
          if (!downloadLink) {
            return Promise.reject("no download links returned from the server");
          }
        })
        .catch((err) => {
          downloadLinksRequested = false;
          alert(`Error while generating a download link: ${err}.\nPlease try again.`);
        });
    }
  }

  function fetchDownloadLinks() {
    return fetch("FIXME")
      .then((resp) => resp.ok && resp.json ?
        resp.json() :
        Promise.reject(`${resp.status} ${resp.statusText}`)
      )
  }
</script>


<h2>Sample bulk download</h2>

{#await batchesPromise}
  <LoadingIndicator />

{:then batchList}
  <form on:submit|preventDefault={onSubmit} >
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
          <input type="checkbox" checked />
          Assemblies
        </label>

        <label>
          <input type="checkbox" checked />
          Annotations
        </label>

        <label class="disabled">
          <input type="checkbox" disabled />
          Reads (not available in the current version)
        </label>
      </fieldset>

      <fieldset disabled={!selectedBatches}>
        <legend>Split download</legend>
        <select>
          {#if selectedBatches}
            <option selected>1 download of 200 GB (1 TB unzipped)</option>
            <option>2 downloads, ~100 GB per download</option>
            <option>4 downloads, ~50 GB per download</option>
            <option>8 downloads, ~25 GB per download</option>
            <option>16 downloads, ~12.5 GB per download</option>
            <option>32 downloads, ~6.2 GB per download</option>
            <option>64 downloads, ~3.1 GB per download</option>
            <option>128 downloads, ~1.6 GB per download</option>
            <option>256 downloads, ~0.8 GB per download</option>
          {/if}
        </select>
      </fieldset>

      <button
        type="submit"
        class="primary"
        disabled={!selectedBatches}
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

