<script>
  import { onMount } from "svelte";
  // We need to import the source Svelte component because Jest doesn't recognise the compiled JS code provided by the library.
  import Select from "svelte-select/src/Select.svelte";
  import { getBatches } from "../../../dataLoading.js";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  const groupBatchesBy = ({ institutionKey }) => institutionKey;

  let allBatches;
  let batchesPromise = Promise.resolve();
  let selectedBatches = null;

  onMount(() => {
    batchesPromise = getBatches(fetch)
      .then((batches) => makeListOfBatches(batches));
  });

  function makeListOfBatches(batches = {}) {
    return Object.keys(batches)
      .map((institutionKey) =>
        batches[institutionKey].deliveries.map((batch) =>
          makeBatchListItem(batch, institutionKey)))
      .flat();
  }

  function makeBatchListItem({ name, date, number: numSamples }, institutionKey) {
    const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
    const batchNameWithData = `${date}: ${name}${numSamplesText}`;
    return {
      label: batchNameWithData,
      value: batchNameWithData,
      institutionKey
    };
  }

  function deselectBatches() {
    selectedBatches = null;
  }

  async function selectBatches() {
    if (!allBatches) {
      const listOfBatches = await batchesPromise;
      allBatches = listOfBatches.map(({ value }) => value);
    }
    selectedBatches = allBatches;
  }
</script>


<h2>Sample bulk download</h2>

{#await batchesPromise}
  <LoadingIndicator />

{:then batchList}
  <form>
    <fieldset>
      <legend>Select batches</legend>

      <button
        type="button"
        on:click={selectBatches}
        class="compact light"
      >
        Select all
      </button>

      <button
        type="button"
        on:click={deselectBatches}
        class="compact light"
      >
        Clear
      </button>

      <Select
        noOptionsMessage={"No batches"}
        bind:value={selectedBatches}
        items={batchList}
        groupBy={groupBatchesBy}
        showIndicator={true}
        isClearable={false}
        isMulti={true}
      />
    </fieldset>

    <fieldset class="data-type-section">
      <legend>Data type</legend>

      <label>
        <input type="checkbox" checked />
        Assemblies
      </label>

      <label>
        <input type="checkbox" checked />
        Annotations
      </label>

      <label>
        <input type="checkbox" />
        Reads ( ⚠️ can increase the size drastically)
      </label>
    </fieldset>
  </form>

{:catch error}
	<p>An unexpected error occured during page loading. Please try again by reloading the page.</p>

{/await}


<style>
form {
  --multiItemActiveBG: transparent;
  --multiItemActiveColor: var(--juno-indigo);
  --multiSelectPadding: 0;
  --multiSelectInputPadding: 0 0 0 .9rem;
}

button {
  margin-bottom: 1rem;
}

.data-type-section {
  display: flex;
  flex-direction: column;
  /* This prevents the checkbox labels from being clickable across all of the container's width. */
  align-items: flex-start;
}
</style>

