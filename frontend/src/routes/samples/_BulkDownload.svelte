<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import debounce from "$lib/utils/debounce.js";
  import {
    getBulkDownloadInfo,
    getBulkDownloadUrls
  } from "$lib/dataLoading.js";

  export let ariaLabelledby;
  export let batches = undefined;

  let downloadEstimate = {};
  let downloadLinksRequested;
  let downloadTokens = [];
  let formValues = {
    annotations: true,
    assemblies: true
  };
  let updateDownloadEstimateTimeoutId;

  $: formComplete = batches?.length &&
      (formValues.annotations || formValues.assemblies);

  // These arguments are passed just to indicate to Svelte that this reactive statement
  // should re-run only when one of the args has changed.
  $: updateDownloadEstimate(batches, formValues);

  function updateDownloadEstimate() {
    unsetDownloadEstimate();
    updateDownloadEstimateTimeoutId = debounce(_updateDownloadEstimate, updateDownloadEstimateTimeoutId);
  }

  function _updateDownloadEstimate() {
    if (!formComplete) {
      return;
    }

    getBulkDownloadInfo(
      batches,
      formValues,
      fetch
    )
      // eslint-disable-next-line no-unused-vars
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

  function onSubmit() {
    if (!formComplete) {
      // Prevents submitting the form on Enter while the confirm btn is disabled.
      return;
    }

    downloadLinksRequested =
      confirm("You won't be able to change the download parameters if you proceed.");
    if (downloadLinksRequested) {
      getBulkDownloadUrls(batches, formValues, fetch)
        .then((downloadLinks = []) => {
          if (downloadLinks.length === 0) {
            console.error("The list of download URLs returned from the server is empty.");
            return Promise.reject();
          }
          const urlSeparator = "/";
          downloadTokens = downloadLinks.map((downloadLink) =>
            downloadLink.split(urlSeparator).pop());
        })
        .catch(() => {
          downloadLinksRequested = false;
          alert("Error while generating a download link. Please try again.");
        });
    }
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

    <fieldset disabled={true}>
      <legend>Estimated total ZIP size</legend>
      <select>
        {#if downloadEstimate?.sizeZipped}
          <option selected>
            {downloadEstimate.sizeZipped}
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
    />
  {/if}
{/if}


<style>
form {
  width: var(--width-reading);
  max-width: 100%;
}

form > fieldset {
  padding: 0;
}

.data-type-section {
  display: flex;
  flex-direction: column;
  /* This prevents the checkbox labels from being clickable across all of the container's width. */
  align-items: flex-start;
}

select {
  min-width: 12rem;
  max-width: 90%;
}

button[type=submit] {
  display: block;
  margin-top: 2.5rem;
  margin-left: .9rem;
}

ol {
  display: flex;
  flex-wrap: wrap;
}
ol li {
  margin-right: 2rem;
  list-style: none;
}

p {
  font-size: .9rem;
  text-align: center;
}

.download-link {
  display: inline-block;
  margin: 2rem 0;
}
.download-link:visited {
  color: var(--color-link-visited);
}
</style>
