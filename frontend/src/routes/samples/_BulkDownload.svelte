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
  let downloadLink;
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
      href={downloadLink}
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

.download-link {
  display: inline-block;
  margin: 2rem 0;
}
</style>
