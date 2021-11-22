<script>
  import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  export let metadataPromise;

  let isError = false;
  let metadata;
  let metadataColumnHeaders = [];

  $: {
    if (metadataPromise) {
    isError = false;
    metadataPromise
      .then((sortedMetadata) => {
        metadata = sortedMetadata;
        metadataColumnHeaders = extractColumnHeadersFromMetadata(sortedMetadata);
      })
      .catch((err) => {
        console.error(err);
        isError = true;
      });
    }
  };

  function extractColumnHeadersFromMetadata(metadata = []) {
    return metadata[0]?.metadata?.map(({ name }) => name);
  }
</script>


{#if metadataPromise}
  <table>
    <tr>
      <!-- `(columnName)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
       https://svelte.dev/docs#each). -->
      {#each metadataColumnHeaders as columnName (columnName)}
        <th>{columnName}<th/>
      {/each}
    </tr>

    {#if isError}
      <tr>
        <!-- FIXME: check that the message is still visible (and accessible) when there are no header columns. -->
        <td colspan={metadataColumnHeaders.length || 1}>
          Error while fetching metadata. Please <a href={`mailto:${EMAIL_MONOCLE_HELP}`}>contact us</a> if the error persists.
        </td>
      </tr>

    {:else if metadata}
      {#each metadata as sample}
        <tr>
          <!-- `(columnName)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
           https://svelte.dev/docs#each). -->
          {#each sample.metadata as { name: columnName, value } (columnName)}
            <td>{value}</td>
          {/each}
        </tr>
      {/each}

    {:else}
      <tr>
        <!-- FIXME: check that the message is still visible (and accessible) when there are no header columns. -->
        <td colspan={metadataColumnHeaders.length || 1}>
          <LoadingIndicator />
        </td>
      </tr>

   {/if}
  </table>
{/if}
