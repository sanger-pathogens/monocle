<script>
  // We need to import the source Svelte component because Jest doesn't recognise the compiled JS code provided by the library.
  import Select from "svelte-select/src/Select.svelte";
  import BinIcon from "$lib/components/icons/BinIcon.svelte";
  import { getDistinctColumnValues } from "$lib/dataLoading.js";
  import { distinctColumnValuesStore, filterStore } from "../_stores.js";

  export let column = undefined;
  let { key: columnKey, dataType: columnDataType } = column || {};

  const initialValuesSet = new Set($filterStore[columnDataType]?.[columnKey]);
  let notMode = false;
  let selectedValues;

  $: values = $distinctColumnValuesStore[columnDataType]?.[columnKey];

  if (!values && column) {
    getDistinctColumnValues([column], fetch)
      .then((distinctValuesResponse) =>
        distinctColumnValuesStore.updateFromDistinctValuesResponse(distinctValuesResponse)
      );
  }

  function applyFilter() {
    filterStore.update((filters) => {
      const selectedValuesAsStrings = selectedValues.map(({ value }) => value);
      const selectedValuesSet = new Set(selectedValuesAsStrings);
      filters[columnDataType][columnKey] = notMode ?
        values.filter((value) => !selectedValuesSet.has(value)) :
        selectedValuesAsStrings;
      return filters;
    });
  }

  function removeAllFilters() {
    if (confirm("Remove filters for ALL columns?")) {
      $filterStore.removeAllFilters();
    }
  }

  function closeFilter() {
    column = undefined;
  }

  function hasChanges() {
    return initialValuesSet.size !== (selectedValues?.length || 0) || (
      !selectedValues?.every(({ value }) => initialValuesSet.has(value))
    );
  }
</script>


{#if column}
  <form aria-live="polite">
    <h4>Filter samples by {column.name}</h4>

    <label>
      Exclude
      <input type="checkbox" bind:checked={notMode} />
    </label>

    <Select
      noOptionsMessage={"No matches"}
      bind:value={selectedValues}
      items={values}
      isWaiting={!values}
      showIndicator={true}
    />

    <button
      class="primary compact"
      type="submit"
      on:click|preventDefault={() => {applyFilter(); closeFilter();}}
      disabled={!hasChanges()}
    >
      Apply and close
    </button>
    <button
      class="primary compact"
      type="submit"
      on:click|preventDefault={applyFilter}
      disabled={!hasChanges()}
    >
      Apply
    </button>
    <button
      class="compact"
      type="button"
      on:click={closeFilter}
    >
      Cancel
    </button>

    <!-- FIXME: a11y -->
    <div class="dropdown-menu">
      <span aria-hidden="true" class="menu-trigger" tabindex="0">
        <BinIcon />
      </span>
      <ul class="menu">
        <li><button
          on:click|preventDefault={() => $filterStore.removeFilter(column)}
          type="submit"
        >
          Remove filter
        </button></li>
        <li><button
          on:click|preventDefault={removeAllFilters}
          type="submit"
        >
          Remove ALL filters
        </button></li>
      </ul>
    </div>
  </form>
{/if}


<style>
.dropdown-menu {
  position: relative;
}
.dropdown-menu .menu {
  display: none;
  list-style: none;
  position: absolute;
}
.menu-trigger {
  cursor: pointer;
}
.menu-trigger:hover ~ .menu,
.menu-trigger:focus ~ .menu {
  display: flex;
}
</style>
