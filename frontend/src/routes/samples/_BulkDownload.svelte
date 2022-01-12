<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import LoadingIcon from "$lib/components/icons/LoadingIcon.svelte";
  import { getBulkDownloadUrls } from "$lib/dataLoading.js";

  let downloadEstimateLatest;
  export let ariaLabelledby;
  export let batches = undefined;
  export { downloadEstimateLatest as downloadEstimate };
  export let formValues;

  let downloadEstimateCurrentDownload;
  let downloadLinksRequested;
  let downloadTokens = [];

  $: estimate = downloadEstimateCurrentDownload || downloadEstimateLatest;

  $: formComplete = batches?.length &&
      (formValues.annotations || formValues.assemblies);

  // Freeze the download estimate once the form is submitted.
  $: {
    if (downloadLinksRequested && !downloadEstimateCurrentDownload) {
      downloadEstimateCurrentDownload = downloadEstimateLatest;
    }
  }

  function onSubmit() {
    if (!formComplete) {
      // Prevents submitting the form on Enter while the confirm btn is disabled.
      return;
    }

    downloadLinksRequested = true;
    getBulkDownloadUrls(batches, formValues, fetch)
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
    downloadEstimateCurrentDownload = null;
    downloadTokens = [];
    downloadLinksRequested = false;
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

      <!-- To be done in a future version of Monocle.
      <label class="disabled">
        <input type="checkbox" />
        Reads ( ⚠️ may increase the size drastically)
      </label>
      -->
    </fieldset>

    <fieldset>
      <dl>
        <dt>Total size:</dt>
        <dd>
          {#if formComplete}
            {#if estimate}
              {estimate.numSamples} sample{estimate.numSamples === 1 ? "" : "s"} of {estimate.sizeZipped}
            {:else}
              <LoadingIcon label="Estimating. Please wait" />
            {/if}
          {:else}
            0
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

    {:else}
      <LoadingIndicator
        message="Please wait: generating a download link can take a while if thousands of samples are involved."
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
  display: flex;
}
dt {
  font-weight: 200;
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
