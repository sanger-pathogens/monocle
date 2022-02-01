<script>
  import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  export let metadataPromise = undefined;

  let isError;
  let isLoading;
  let metadata;
  let metadataColumnHeaders = [];

  $: {
    if (metadataPromise) {
      isError = false;
      isLoading = true;
      metadataPromise
        .then((sortedMetadata) => {
          metadata = sortedMetadata;
          metadataColumnHeaders = extractColumnHeadersFromMetadata(sortedMetadata);
        })
        .catch((err) => {
          console.error(err);
          isError = true;
        })
        .finally(() => isLoading = false);
    }
  }

  function extractColumnHeadersFromMetadata(metadata = []) {
    return metadata[0]?.metadata?.map(({ title }) => title) || [];
  }
</script>


{#if metadataPromise}
  <table class="dense">
    <tr>
      <!-- `(columnTitle)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
       https://svelte.dev/docs#each). -->
      {#each metadataColumnHeaders as columnTitle (columnTitle)}
        <th>{columnTitle}</th>
      {/each}
    </tr>

    {#if isError}
      <tr>
        <td colspan={metadataColumnHeaders.length || 1}>
          Error while fetching metadata. Please <a href={`mailto:${EMAIL_MONOCLE_HELP}`}>contact us</a> if the error persists.
        </td>
      </tr>

    {:else}

      {#if metadata?.length}
        {#each metadata as sample}
          <tr class="data-row" class:loading={isLoading} aria-live="polite">
            <!-- `(columnTitle)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
             https://svelte.dev/docs#each). -->
            {#each sample.metadata as { title: columnTitle, value } (columnTitle)}
              <td>{value}</td>
            {/each}
          </tr>
        {/each}
      {:else if !isLoading}
        <tr>
          <td class="no-data-row" colspan={metadataColumnHeaders.length || 1}>
            No data. Try to refresh or change a filter.
          </td>
        </tr>
      {/if}

      {#if isLoading}
        <tr class="loading-indicator-row" class:no-metadata={!metadata || metadata.length === 0}>
          <td colspan={metadataColumnHeaders.length || 1}>
            <LoadingIndicator />
          </td>
        </tr>
      {/if}

    {/if}
  </table>
{/if}


<style>
table {
  display: block;
  min-height: 9rem;
  overflow-x: auto;
  position: relative;
}

.loading-indicator-row {
  position: absolute;
  bottom: 38%;
  left: 40%;
}
.loading-indicator-row.no-metadata {
  bottom: 5%;
}

.data-row.loading {
  opacity: .27;
}

.data-row:nth-child(odd) {
  background: var(--color-table-alt-row);
}

.data-row:hover {
  background: var(--color-table-hover-row);
}

.no-data-row {
  text-align: center;
}
</style>
