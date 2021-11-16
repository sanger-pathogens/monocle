<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  export let metadataPromise;

  let metadataColumnHeaders = [];

  metadataPromise
    .then((metadata) =>
      // Extract column headers from metadata or fall back to headers from the previous response.
      metadataColumnHeaders = extractColumnHeadersFromMetadata(metadata) || metadataColumnHeaders;
    );

  function extractColumnHeadersFromMetadata(metadata = []) {
    return metadata[0]?.metadata?.map(({ name }) => name);
  }
</script>


<table>
  <tr>
    <!-- `(columnName)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
     https://svelte.dev/docs#each). -->
    {#each metadataColumnHeaders as columnName (columnName)}
      <th>{columnName}<th/>
    {/each}
  </tr>

  {#await metadataPromise}
    <LoadingIndicator />

  {:then metadata}
    {#each metadata as sample}
      <tr>
        <!-- `("<column name>-<value>")` is a unique (per sample) key for Svelte to identify cells to avoid unnecessary
         re-rendering (see https://svelte.dev/docs#each). -->
        {#each sample.metadata as { name: columnName, value } (`${columnName}-${value}`)}
          <td>{value}</td>
        {/each}
      </tr>
    {/each}

  {:catch}
    <p></p>

  {/await}
</table>
