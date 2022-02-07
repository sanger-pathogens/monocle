<script>
  import { filterStore } from "../_stores.js";

  export let column;
  export let screenReaderOnly = false;

  function removeAllFilters() {
    if (confirm("Remove filters for ALL columns?")) {
      filterStore.removeAllFilters();
    }
  }
</script>


{#if screenReaderOnly}
  <button
    aria-hidden="false"
    on:click={() => filterStore.removeFilter(column)}
    class="sr-only"
  >
    Remove filter
  </button>
  <button
    aria-hidden="false"
    on:click={removeAllFilters}
    class="sr-only"
  >
    Remove all filters
  </button>

{:else}
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
{/if}


<style>
button {
  border: none;
  margin-right: 0;
}
button:last-child {
  margin-bottom: .2rem;
}
</style>
