<script>
  // We need to import the source Svelte component because Jest doesn't recognise the compiled JS code provided by the library.
  import Select from "svelte-select/src/Select.svelte";

  const STYLE_SELECT_CONTAINER = `
    flex-grow: 1;
    align-self: baseline;
    width: 100%
  `;

  export let batchList;
  export let selectedBatches = null;

  let allBatches;

  function deselectBatches() {
    selectedBatches = null;
  }

  function selectBatches() {
    if (!allBatches) {
      allBatches = Array.from(batchList);
    }
    selectedBatches = allBatches;
  }

  function groupBatchesBy({ group }) {
    return group;
  }
</script>

<div class="container">
  <Select
    noOptionsMessage={"No batches"}
    bind:value={selectedBatches}
    items={batchList}
    groupBy={groupBatchesBy}
    showIndicator={true}
    isClearable={false}
    isMulti={true}
    containerStyles={STYLE_SELECT_CONTAINER}
  />

  <div class="buttons-container">
    <button type="button" on:click={selectBatches} class="compact">
      Select all
    </button>

    <button type="button" on:click={deselectBatches} class="compact">
      Clear
    </button>
  </div>
</div>

<style>
  :root {
    --multiItemActiveBG: transparent;
    --multiItemActiveColor: var(--juno-indigo);
    --multiSelectPadding: 0;
    --multiSelectInputPadding: 0 0 0 0.9rem;
  }

  .container {
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    margin-left: auto;
    margin-right: auto;
    max-width: 44rem;
  }

  .buttons-container {
    display: flex;
    flex-shrink: 0;
    margin-left: 0.5rem;
    order: -1;
  }

  @media (min-width: 480px) {
    .container {
      flex-direction: row;
    }

    .buttons-container {
      flex-direction: column;
      order: 0;
    }
  }

  button {
    flex-shrink: 0;
  }
</style>
