<script>
  import { onMount } from "svelte";
  // We need to import the source Svelte component because Jest doesn't recognise the compiled JS code provided by the library.
  import Select from "svelte-select/src/Select.svelte";
  import BinIcon from "$lib/components/icons/BinIcon.svelte";
  import { getDistinctColumnValues } from "$lib/dataLoading.js";
  import { distinctColumnValuesStore, filterStore } from "../_stores.js";

  export let column = undefined;
  let { name: columnName, dataType: columnDataType } = column || {};

  const NARROW_SCREEN_BREAKPOINT = 600;

  let filterContainerElement;
  let exclude = false;
  let selectedValues = $filterStore[columnDataType]?.[columnName]?.map(
    (value) => ({ label: value, value }));

  // FIXME: account for exclude
  $: hasChanges = true || savedState.exclude !== exclude ||
    savedState.values.size !== (selectedValues?.length || 0) ||
    selectedValues && !selectedValues.every(({ value }) => savedState.values.has(value));
  // Save filter state for `hasChanges` each time a filter is applied or removed.
  $: savedState = getState($filterStore[columnDataType]?.[columnName]);
  $: values = $distinctColumnValuesStore[columnDataType]?.[columnName];

  if (!values && column) {
    getDistinctColumnValues([column], fetch)
      .then((distinctValuesResponse) =>
        distinctColumnValuesStore.updateFromDistinctValuesResponse(distinctValuesResponse)
      );
  }

  // Waiting for the component to "mount" because we need DOM element `filterContainerElement` to be present.
  onMount(() => {
    const screenWidth = document.documentElement.clientWidth;
    if (screenWidth <= NARROW_SCREEN_BREAKPOINT) {
      //FIXME
    }
    else if (isFilterPastMiddleOfScreen(screenWidth)) {
      positionFilterToLeftOfNextColumn();
    }
  });

  function applyFilter() {
    filterStore.update((filters) => {
      const selectedValuesAsStrings = selectedValues?.map(({ value }) => value) || [];
      const selectedValuesSet = new Set(selectedValuesAsStrings);
      filters[columnDataType][columnName] = exclude ?
        values.filter((value) => !selectedValuesSet.has(value)) :
        selectedValuesAsStrings;
      return filters;
    });
  }

  function removeAllFilters() {
    if (confirm("Remove filters for ALL columns?")) {
      filterStore.removeAllFilters();
    }
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

  function getState() {
    return {
      values: new Set($filterStore[columnDataType]?.[columnName]),
      exclude
    };
  }
</script>


<article
  role="dialog"
  aria-labelledby="filter-menu-heading"
  bind:this={filterContainerElement}
>
  <h4 id="filter-menu-heading">Filter samples by {column.title}</h4>

  <label>
    Exclude selected values
    <input type="checkbox" bind:checked={exclude} />
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
    disabled={!hasChanges}
  >
    Apply and close
  </button>
  <button
    class="primary compact"
    on:click={applyFilter}
    disabled={!hasChanges}
  >
    Apply
  </button>
  <button
    class="compact"
    on:click={closeFilter}
  >
    Close
  </button>

  <!-- FIXME: a11y -->
  <span class="dropdown-menu">
    <span aria-hidden="true" class="menu-trigger" tabindex="0">
      <BinIcon />
    </span>
    <div class="menu">
      <button
        on:click={() => filterStore.removeFilter(column)}
        class="compact"
      >
        Remove filter
      </button>
      <button
        on:click={removeAllFilters}
        class="danger compact"
      >
        Remove all filters
      </button>
    </div>
  </span>
</article>


<style>
article {
  position: absolute;
  top: 2.2rem;
  background: var(--background-body);
  border: 1px solid var(--color-border);
  box-shadow: -2px 2px 8px 0 rgba(0, 0, 0, .2);
  padding: 0 1.2rem .6rem;
  width: 25rem;
  max-width: 98vw;
}

h4 {
  margin-top: revert;
}

.dropdown-menu {
  float: right;
  margin-top: .4rem;
  position: relative;
}
.menu {
  background: var(--background-body);
  border: 1px solid var(--color-border);
  box-shadow: -2px 2px 8px 0 rgba(0, 0, 0, .2);
  display: none;
  list-style: none;
  position: absolute;
  transform: translateX(-44%);
}
.menu button {
  border: none;
  margin-right: 0;
}
.menu button:last-child {
  margin-bottom: .2rem;
}
.menu-trigger {
  cursor: pointer;
  padding: 0 1rem .5rem;
}
.dropdown-menu:focus-within .menu,
.menu-trigger:hover ~ .menu,
.menu-trigger:focus ~ .menu,
.menu:hover {
  display: flex;
  flex-direction: column;
}
</style>
