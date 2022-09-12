<script>
  import { DATA_TYPES, MONOCLE_HELP_EMAIL } from "$lib/constants.js";
  import FilterIcon from "$lib/components/icons/FilterIcon.svelte";
  import FilterMenuIcon from "$lib/components/icons/FilterMenuIcon.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import Filter from "./_Filter.svelte";
  import {
    displayedColumnsStore,
    distinctColumnValuesStore,
    filterStore,
  } from "../_stores.js";

  export let batches;
  export let metadataPromise = undefined;

  const COLOR_INACTIVE_FILTER = "silver";
  const EMPTY_STRING = "";
  const NARROW_SCREEN_BREAKPOINT = 880;

  let columnOfOpenFilter;
  let isError;
  let isLoading;
  let metadata;
  let screenWidth = window?.innerWidth || NARROW_SCREEN_BREAKPOINT + 1;

  $: columnHeaders = getColumnHeadersFromDisplayedColumnsState(
    $displayedColumnsStore
  );

  $: {
    distinctColumnValuesStore.reset(batches);
  }

  $: {
    if (metadataPromise) {
      isError = false;
      isLoading = true;
      metadataPromise
        .then((sortedMetadata) => {
          metadata = sortedMetadata.map(fillSampleWithMissingTrailingFields);
        })
        .catch((err) => {
          console.error(err);
          isError = true;
        })
        .finally(() => (isLoading = false));
    }
  }

  function getColumnHeadersFromDisplayedColumnsState(
    displayedColumnsState = {}
  ) {
    return DATA_TYPES.reduce((columnAccumulator, dataType) => {
      const storedColumns = displayedColumnsState[dataType];
      if (storedColumns?.length) {
        for (const column of storedColumns) {
          columnAccumulator.push({ ...column, dataType });
        }
      }
      return columnAccumulator;
    }, []);
  }

  function fillSampleWithMissingTrailingFields(sample) {
    const numColumns = columnHeaders.length;
    const numMissingFields = numColumns - sample.length;
    if (numMissingFields > 0) {
      while (sample.length < numColumns) {
        sample.push(columnHeaders[sample.length]);
      }
    }
    return sample;
  }

  function toggleFilterMenu(clickedColumn) {
    if (!columnOfOpenFilter) {
      columnOfOpenFilter = clickedColumn;
      return;
    }
    const isSameColumn =
      columnOfOpenFilter.name === clickedColumn.name &&
      columnOfOpenFilter.dataType === clickedColumn.dataType;
    if (isSameColumn) {
      closeFilter();
    } else {
      columnOfOpenFilter = clickedColumn;
    }
  }

  function closeFilter() {
    columnOfOpenFilter = undefined;
  }
</script>

<svelte:window
  on:resize={() => {
    screenWidth = window.innerWidth;
  }}
/>

{#if metadataPromise}
  <table
    class={`dense ${
      screenWidth > NARROW_SCREEN_BREAKPOINT && columnHeaders.length < 6
        ? "few-columns"
        : EMPTY_STRING
    }`}
  >
    <tr>
      <!-- `(<unique key>)` is a key for Svelte to identify cells to avoid unnecessary re-rendering (see
       https://svelte.dev/docs#template-syntax-each). -->
      {#each columnHeaders as column (`${column.name}:${column.dataType}`)}
        {@const { displayName: columnDisplayName } = column}
        <th>
          {columnDisplayName}
          <button
            aria-label="Toggle the filter menu for column {columnDisplayName}"
            title="Toggle filter menu"
            on:click={() => toggleFilterMenu(column)}
            class="filter-btn"
          >
            {#if columnOfOpenFilter?.displayName !== columnDisplayName}
              <FilterIcon
                width="17"
                height="17"
                color={$filterStore[column.dataType][column.name]
                  ? null
                  : COLOR_INACTIVE_FILTER}
              />
            {:else}
              <FilterMenuIcon
                width="17"
                height="17"
                color={$filterStore[column.dataType][column.name]
                  ? null
                  : COLOR_INACTIVE_FILTER}
              />
            {/if}
          </button>
          {#if columnOfOpenFilter && columnOfOpenFilter.displayName === columnDisplayName}
            <Filter {batches} bind:column={columnOfOpenFilter} />
          {/if}
        </th>
      {/each}
    </tr>

    {#if isError}
      <tr>
        <td colspan={columnHeaders.length || 1} class="error-msg">
          An error occured while fetching metadata. Please <a
            href={`mailto:${MONOCLE_HELP_EMAIL}`}>contact us</a
          > if the error persists.
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
              <td
                ><div>
                  {column.value === undefined || column.value === null
                    ? EMPTY_STRING
                    : column.value}
                </div></td
              >
            {/each}
          </tr>
        {/each}
      {:else if !isLoading}
        <tr>
          <td class="no-data" colspan={columnHeaders.length || 1}>
            No samples found. Try different batches or filters.
          </td>
        </tr>
      {/if}

      {#if isLoading}
        <tr
          class="loading-indicator-row"
          class:no-metadata={!metadata || metadata.length === 0}
        >
          <td colspan={columnHeaders.length || 1}>
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

  .error-msg,
  .no-data {
    padding-top: 3rem;
  }

  .filter-btn {
    border: none;
    margin: 0;
    padding: 0.1rem 0.2rem 0;
    position: relative;
    top: 0.1rem;
  }

  .loading-indicator-row {
    position: absolute;
    bottom: 32%;
    left: 42%;
  }
  .loading-indicator-row.no-metadata {
    bottom: 36%;
  }

  .data-row.loading {
    opacity: 0.27;
  }

  .data-row:nth-child(odd) {
    background: var(--color-table-alt-row);
  }

  .data-row:hover {
    background: var(--color-table-hover-row);
  }
</style>
