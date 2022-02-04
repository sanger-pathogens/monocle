<script>
  import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
  import FilterIcon from "$lib/components/icons/FilterIcon.svelte";
  import FilterMenuIcon from "$lib/components/icons/FilterMenuIcon.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import Filter from "./_Filter.svelte";
  import { filterStore } from "../_stores.js";

  export let metadataPromise = undefined;

  const COLOR_INACTIVE_FILTER = "silver";
  const DATA_TYPE_METADATA = "metadata";

  let columnOfOpenFilter;
  let isError;
  let isLoading;
  let metadata;
  let columns = [];

  $: {
    if (metadataPromise) {
      isError = false;
      isLoading = true;
      metadataPromise
        .then((sortedMetadata) => {
          metadata = sortedMetadata;
          columns = extractColumnsFromMetadata(sortedMetadata);
        })
        .catch((err) => {
          console.error(err);
          isError = true;
        })
        .finally(() => isLoading = false);
    }
  }

  function extractColumnsFromMetadata(sortedMetadata = []) {
    return sortedMetadata[0]?.[DATA_TYPE_METADATA]?.map(
      ({ name, title }) => ({ name, title, dataType: DATA_TYPE_METADATA })
    ) || [];
  }

  function toggleFilterMenu(clickedColumn) {
    if (!columnOfOpenFilter) {
      columnOfOpenFilter = clickedColumn;
      return;
    }
    const isSameColumn = columnOfOpenFilter.name === clickedColumn.name && columnOfOpenFilter.dataType === clickedColumn.dataType;
    columnOfOpenFilter = isSameColumn ? undefined : clickedColumn;
  }
</script>


{#if metadataPromise}
  <table class="dense">
    <tr>
      <!-- `(<unique key>)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
       https://svelte.dev/docs#template-syntax-each). -->
      {#each columns as column (`${column.name}:${column.dataType}`)}
        {@const { title: columnTitle } = column}
        <th>
          {columnTitle}
          <button
            aria-label="Toggle the filter menu for column {columnTitle}"
            title="Toggle filter menu"
            on:click={() => toggleFilterMenu(column)}
            class="filter-btn"
          >
            {#if columnOfOpenFilter?.title !== columnTitle}
              <FilterIcon width="17" height="17" color={$filterStore[column.dataType][column.name] ? null : COLOR_INACTIVE_FILTER} />
            {:else}
              <FilterMenuIcon width="17" height="17" color={$filterStore[column.dataType][column.name] ? null : COLOR_INACTIVE_FILTER} />
            {/if}
          </button>
          {#if columnOfOpenFilter?.title === columnTitle}
            <Filter bind:column={columnOfOpenFilter} />
          {/if}
        </th>
      {/each}
    </tr>

    {#if isError}
      <tr>
        <td colspan={columns.length || 1} class="error-msg">
          An error occured while fetching metadata. Please <a href={`mailto:${EMAIL_MONOCLE_HELP}`}>contact us</a> if the error persists.
        </td>
      </tr>

    {:else}

      {#if metadata?.length}
        {#each metadata as sample}
          <tr class="data-row" class:loading={isLoading} aria-live="polite">
            <!-- `(<unique key>)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
             https://svelte.dev/docs#template-syntax-each). -->
            {#each sample.metadata as metadata (`${metadata.name}:metadata`)}
              <td>{metadata.value}</td>
            {/each}
          </tr>
        {/each}
      {:else if !isLoading}
        <tr>
          <td class="no-data-row" colspan={columns.length || 1}>
            No data. Try to refresh or change a filter.
          </td>
        </tr>
      {/if}

      {#if isLoading}
        <tr class="loading-indicator-row" class:no-metadata={!metadata || metadata.length === 0}>
          <td colspan={columns.length || 1}>
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
  min-height: 21rem;
  overflow-x: auto;
  position: relative;
}

th {
  /* Column headers must remain `relative`ly positioned for the filter to be correctly positioned for rightmost headers. */
  position: relative;
  white-space: nowrap;
}

.error-msg {
  padding-top: 3rem;
}

.filter-btn {
  border: none;
  margin: 0;
  padding: .1rem .2rem 0;
  position: relative;
  top: .1rem;
}

.loading-indicator-row {
  position: absolute;
  bottom: 30%;
  left: 43%;
}
.loading-indicator-row.no-metadata {
  bottom: 50%;
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
