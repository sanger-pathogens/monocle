<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import LoadingIcon from "$lib/components/icons/LoadingIcon.svelte";
  import { deepCopy } from "$lib/utils/copy.js";
  import { getBulkDownloadUrls } from "$lib/dataLoading.js";
  import MetadataDownloadButton from "./_MetadataDownloadButton.svelte";
  import { distinctColumnValuesStore, filterStore } from "./_stores.js";

  let _downloadEstimate = undefined;
  export let ariaLabelledby;
  export let batches = undefined;
  export { _downloadEstimate as downloadEstimate };
  export let formValues;

  let downloadLinksRequested;
  let downloadTokens = [];
  let estimate = _downloadEstimate;
  let downloadBatches;
  let downloadFilterState;
  let downloadDistinctColumnValuesState;

  $: shouldFreezeDownloadEstimate = _shouldFreezeDownloadEstimate(batches, $filterStore);

  $: {
    if (!shouldFreezeDownloadEstimate) {
      estimate = _downloadEstimate;
    }
  }

  $: maxSamplesPerZipSelection = estimate?.sizePerZipOptions?.[0]?.maxSamplesPerZip;

  $: formComplete = batches?.length &&
    (formValues.annotations || formValues.assemblies || formValues.reads);

  function onSubmit() {
    if (!formComplete) {
      // Prevents submitting the form on Enter while the confirm btn is disabled.
      return;
    }

    // Save batches, filter, and distinct values for metadata download so that it uses them
    // "frozen" at the time of submit, not the latest ones (which can be different if e.g. the user closes
    // the bulk download dialog and changes the filter w/o resetting the bulk download).
    downloadBatches = deepCopy(batches);
    downloadFilterState = deepCopy($filterStore);
    downloadDistinctColumnValuesState = deepCopy($distinctColumnValuesStore);
    downloadLinksRequested = true;
    getBulkDownloadUrls({
      instKeyBatchDatePairs: batches,
      filter: { filterState: downloadFilterState, distinctColumnValuesState: downloadDistinctColumnValuesState },
      ...formValues,
      maxSamplesPerZip: maxSamplesPerZipSelection
    }, fetch)
      .then((downloadLinks = []) => {
        // If the form has been reset meanwhile, do nothing.
        if (!downloadLinksRequested) {
          return;
        }

        if (downloadLinks.length === 0) {
          console.error("The list of download URLs returned from the server is empty.");
          return Promise.reject();
        }
        const urlSeparator = "/";
        downloadTokens = downloadLinks.map((downloadLink) =>
          downloadLink.split(urlSeparator).pop());
      })
      .catch(() => {
        resetForm();
        alert("Error while generating a download link. Please try again.");
      });
  }

  function resetForm() {
    downloadTokens = [];
    downloadLinksRequested = false;
    shouldFreezeDownloadEstimate = false;
  }

  function _shouldFreezeDownloadEstimate() {
    return downloadLinksRequested && Boolean(estimate);
  }
</script>


<form
  aria-labelledby={ariaLabelledby}
  on:submit|preventDefault={onSubmit}
>
  <fieldset
    disabled={downloadLinksRequested}
    class:disabled={downloadLinksRequested}
  >
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

      <label>
        <input
          type="checkbox"
          bind:checked={formValues.reads}
        />
        Reads ( ⚠️ may increase the total size drastically)
      </label>
    </fieldset>

    <fieldset>
      <dl>
        <dt>Total size:</dt>
        <dd>
          {#if formComplete}
            {#if estimate}
              {estimate.sizeZipped} ({estimate.numSamples} sample{estimate.numSamples === 1 ? "" : "s"})
            {:else}
              <LoadingIcon label="Estimating the download size. Please wait" />
            {/if}
          {:else}
            0
          {/if}
        </dd>

        <dt>Maximum size per ZIP archive:</dt>
        <dd>
          {#if formComplete}
            {#if estimate}
              <select bind:value={maxSamplesPerZipSelection} disabled={estimate.sizePerZipOptions?.length <= 1}>
                {#each estimate.sizePerZipOptions as { sizePerZip, maxSamplesPerZip } (`${sizePerZip}${maxSamplesPerZip}`)}
                  {@const numZips = Math.ceil(estimate.numSamples / maxSamplesPerZip)}
                  <option value={maxSamplesPerZip}>
                    {sizePerZip} ({numZips} ZIP archive{numZips === 1 ? "" : "s"})
                  </option>
                {/each}
              </select>
            {:else}
              <LoadingIcon label="Estimating the download size. Please wait" />
            {/if}
          {:else}
            <select disabled>
              <option>0</option>
            </select>
          {/if}
        </dd>
      </dl>
    </fieldset>
  </fieldset>

  <button
    type="submit"
    class="primary"
    disabled={!formComplete || downloadLinksRequested}
  >
    Confirm
  </button>

  {#if downloadLinksRequested}
    <button
      type="button"
      class="compact"
      on:click={resetForm}
    >
      Reset
    </button>
  {/if}
</form>

{#if downloadLinksRequested}
  <div class="links-section">
    {#if downloadTokens.length > 1}
      <h3>Download links</h3>
      <ol>
        {#each downloadTokens as downloadToken, i (downloadToken)}
          <li>
            <a
              href="/samples/download/{downloadToken}"
              target="_blank"
              class="download-link"
            >
              ZIP archive {i + 1} of {downloadTokens.length}
            </a>
          </li>
        {/each}
      </ol>

    {:else if downloadTokens.length}
      <a
        href="/samples/download/{downloadTokens[0]}"
        target="_blank"
        class="download-link"
      >
        Download ZIP archive
      </a>
    {/if}

    <MetadataDownloadButton
      batches={downloadBatches}
      fileNameWithoutExtension={"monocle-metadata-from-sample-download"}
      filterState={downloadFilterState}
      distinctColumnValuesState={downloadDistinctColumnValuesState}
      style="display: block; margin-bottom: 1.2rem"
    />

    {#if !downloadTokens.length}
      <LoadingIndicator
        message="Please wait: generating ZIP download links can take a while if thousands of samples are involved."
        simple={true}
      />
    {/if}
  </div>
{/if}


<style>
form {
  margin-bottom: 1.5rem;
  width: var(--width-reading);
  max-width: 100%;
}

form > fieldset {
  margin-bottom: 0;
  padding: 0;
}

.data-type-section {
  display: flex;
  flex-direction: column;
  /* This prevents the checkbox labels from being clickable across all of the container's width. */
  align-items: flex-start;
}

dl {
  display: grid;
  grid-template-columns: 1fr 2fr;
  row-gap: 1em;
}
dt {
  font-weight: 200;
}

.disabled select:disabled {
  opacity: 1;
}

button[type=submit] {
  display: inline-block;
  margin-top: 2.5rem;
  margin-left: .9rem;
  margin-right: 1rem;
}

ol {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 0;
  padding-left: 1rem;
}
ol li {
  margin-right: 2rem;
  list-style: none;
}

.links-section {
  margin-left: 1rem;
}

.download-link {
  display: inline-block;
  margin: 2rem 0;
}
.download-link:visited {
  color: var(--color-link-visited);
}
</style>
