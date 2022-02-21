<script>
  import { onMount } from "svelte";
  // We need to import the source Svelte component because Jest doesn't recognise the compiled JS code provided by the library.
  import Select from "svelte-select/src/Select.svelte";
  import RemoveFilterIcon from "$lib/components/icons/RemoveFilterIcon.svelte";
  import { getDistinctColumnValues } from "$lib/dataLoading.js";
  import { distinctColumnValuesStore, filterStore } from "../_stores.js";

  export let batches;
  export let column;
  let { name: columnName, dataType: columnDataType } = column || {};

  const NARROW_SCREEN_BREAKPOINT = 810;

  let filterContainerElement;
  let exclude = $filterStore[columnDataType][columnName]?.exclude || false;
  let selectedValues = $filterStore[columnDataType][columnName]?.values.map(
    (value) => ({ label: value, value }));

  $: hasChanges = _hasChanges(savedState, selectedValues, exclude);
  // Save filter state for `hasChanges` each time a filter is applied or removed.
  $: savedState = $filterStore[columnDataType][columnName] || { values: [] };
  $: values = $distinctColumnValuesStore[columnDataType]?.[columnName];

  $: {
    if (!values && column) {
      getDistinctColumnValues({
        instKeyBatchDatePairs: batches,
        columns: [column],
        filter: { filterState: $filterStore, distinctColumnValues: $distinctColumnValuesStore },
      }, fetch)
        .then((distinctValuesResponse) =>
          distinctColumnValuesStore.updateFromDistinctValuesResponse(distinctValuesResponse)
        );
    }
  }

  // Waiting for the component to "mount" because we need DOM element `filterContainerElement` to be present.
  onMount(() => {
    const screenWidth = document.documentElement.clientWidth;
    if (screenWidth <= NARROW_SCREEN_BREAKPOINT) {
      positionFilterLeftmost();
    }
    else if (isFilterPastMiddleOfScreen(screenWidth)) {
      positionFilterToLeftOfNextColumn();
    }
  });

  function applyFilter() {
    filterStore.update((filters) => {
      filters[columnDataType][columnName] = {
        values: selectedValues?.map(({ value }) => value) || [],
        exclude
      };
      return filters;
    });
  }

  function closeFilter() {
    column = undefined;
  }

  function isFilterPastMiddleOfScreen(screenWidth) {
    return filterContainerElement.getBoundingClientRect().left > screenWidth / 2;
  }

  function positionFilterToLeftOfNextColumn() {
    filterContainerElement.style.right = "0";
  }

  function positionFilterLeftmost() {
    filterContainerElement.style.left =
      `-${filterContainerElement.parentNode.getBoundingClientRect().left - 21}px`;
  }

  function _hasChanges() {
    if (Boolean(savedState.exclude) !== exclude && selectedValues?.length) {
      return true;
    }
    const savedStateValuesSet = new Set(savedState.values);
    return savedStateValuesSet.size !== (selectedValues?.length || 0) ||
      selectedValues && !selectedValues.every(({ value }) => savedStateValuesSet.has(value));
  }
</script>


{#if column}
  <article
    role="dialog"
    aria-labelledby="filter-menu-heading"
    bind:this={filterContainerElement}
  >
    <h4 id="filter-menu-heading">Filter samples by {column.title}</h4>

    <label>
      <input type="checkbox" bind:checked={exclude} disabled={!values || values.length === 1} />
      <em>Exclude</em> samples with the selected values
    </label>

    <Select
      noOptionsMessage={"No matches"}
      isMulti={true}
      bind:value={selectedValues}
      items={values}
      isWaiting={!values}
      showIndicator={true}
      containerStyles="margin-bottom: 2.2rem"
    />

    <button
      class="primary compact"
      on:click={() => {applyFilter(); closeFilter();}}
      disabled={!values || !hasChanges}
    >
      Apply and close
    </button>
    <button
      class="primary compact"
      on:click={applyFilter}
      disabled={!values || !hasChanges}
    >
      Apply
    </button>
    <button
      class="compact"
      on:click={closeFilter}
    >
      Close
    </button>
    <button
      title="Remove this filter"
      aria-label={`Remove the filter for column ${column.title}`}
      on:click={() => filterStore.removeFilter(column)}
      class="remove-filter-btn icon-btn"
      disabled={! $filterStore[columnDataType][columnName]}
    >
      <RemoveFilterIcon />
    </button>
  </article>
{/if}


<style>
article {
  position: absolute;
  top: 2.2rem;
  background: var(--background-body);
  border: 1px solid var(--color-border);
  box-shadow: -2px 2px 8px 0 rgba(0, 0, 0, .2);
  padding: 0 1.2rem .6rem;
  width: 25rem;
  max-width: 83vw;
  /* This value should be less than `z-index` in the dialog component, lest the filter is shown on top of the bulk download dialog. */
  z-index: 5;
}

h4 {
  margin-top: revert;
}

.remove-filter-btn {
  float: right;
}
</style>
