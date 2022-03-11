<script>
  import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
  import FilterIcon from "$lib/components/icons/FilterIcon.svelte";
  import FilterMenuIcon from "$lib/components/icons/FilterMenuIcon.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import Filter from "./_Filter.svelte";
  import { distinctColumnValuesStore, filterStore } from "../_stores.js";

  export let batches;
  export let metadataPromise = undefined;

  const COLOR_INACTIVE_FILTER = "silver";
  const NARROW_SCREEN_BREAKPOINT = 880;

  let columnOfOpenFilter;
  let isError;
  let isLoading;
  let metadata;
  let columns = [];
  let screenWidth = window?.innerWidth || NARROW_SCREEN_BREAKPOINT + 1;

  $: { distinctColumnValuesStore.reset(batches); }

  $: {
    if (metadataPromise) {
      isError = false;
      isLoading = true;
      metadataPromise
        .then((sortedMetadata) => {
          metadata = sortedMetadata;
          // Only uodate columns if there are data in the response.
          if (sortedMetadata.length) {
            columns = sortedMetadata[0];
          }
        })
        .catch((err) => {
          console.error(err);
          isError = true;
        })
        .finally(() => isLoading = false);
    }
  }

  $: {
    if (columns.length === 0) {
      closeFilter();
    }
  }

  function toggleFilterMenu(clickedColumn) {
    if (!columnOfOpenFilter) {
      columnOfOpenFilter = clickedColumn;
      return;
    }
    const isSameColumn = columnOfOpenFilter.name === clickedColumn.name && columnOfOpenFilter.dataType === clickedColumn.dataType;
    if (isSameColumn) {
      closeFilter();
    }
    else {
      columnOfOpenFilter = clickedColumn;
    }
  }

  function closeFilter() {
    columnOfOpenFilter = undefined;
  }
</script>


<svelte:window on:resize={() => {screenWidth = window.innerWidth;}} />

{#if metadataPromise}
  <table class={`dense ${screenWidth > NARROW_SCREEN_BREAKPOINT && columns.length < 6 ? "few-columns" : ""}`}>
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
          {#if columnOfOpenFilter && columnOfOpenFilter.title === columnTitle}
            <Filter {batches} bind:column={columnOfOpenFilter} />
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
            {#each sample as column (`${column.name}:${column.dataType}`)}
              <!-- The inner <div /> is needed to impose a maximum height on a table cell. -->
              <td><div>{column.value === null ? "" : column.value}</div></td>
            {/each}
          </tr>
        {/each}
      {:else if !isLoading}
        <tr>
          <td class="no-data" colspan={columns.length || 1}>
            No samples found. Try different batches or filters.
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
  min-height: 23rem;
  overflow-x: auto;
  position: relative;
}
.few-columns {
  /* `display: table` is needed to force a full width on the table if there are few columns. */
  display: table;
}

th {
  /* Column headers must remain `relative`ly positioned for the filter to be correctly positioned for rightmost headers. */
  position: relative;
  white-space: nowrap;
}

td > div {
  max-height: 3.1rem;
  overflow-y: auto;
}

.error-msg, .no-data {
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
  bottom: 32%;
  left: 42%;
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
</style>
