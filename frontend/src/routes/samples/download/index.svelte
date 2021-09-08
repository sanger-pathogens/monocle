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

  function onSubmit() {
    confirm("You won't be able to change the parameters if you proceed.");
  }
</script>


<h2>Sample bulk download</h2>

{#await batchesPromise}
  <LoadingIndicator />

{:then batchList}
  <form on:submit|preventDefault={onSubmit}>

    <fieldset class="batch-selection-section">
      <legend>Select batches to download</legend>

      <div>
        <button
          type="button"
          on:click={selectBatches}
          class="compact"
        >
          Select all
        </button>

        <button
          type="button"
          on:click={deselectBatches}
          class="compact"
        >
          Clear
        </button>
      </div>

      <Select
        noOptionsMessage={"No batches"}
        bind:value={selectedBatches}
        items={batchList}
        groupBy={groupBatchesBy}
        showIndicator={true}
        isClearable={false}
        isMulti={true}
        containerStyles="flex-grow: 1; order: -1"
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
        Reads ( ⚠️ may increase the size drastically)
      </label>
    </fieldset>

    <fieldset disabled={!selectedBatches}>
      <legend>Split download</legend>
      <select>
        {#if selectedBatches}
          <option selected>1 download of 200 GB (1 TB unzipped)</option>
          <option>2 downloads, ~100 GB per download</option>
          <option>4 downloads, ~50 GB per download</option>
          <option>8 downloads, ~25 GB per download</option>
          <option>16 downloads, ~12.5 GB per download</option>
          <option>32 downloads, ~6.2 GB per download</option>
          <option>64 downloads, ~3.1 GB per download</option>
          <option>128 downloads, ~1.6 GB per download</option>
          <option>256 downloads, ~0.8 GB per download</option>
        {/if}
      </select>
    </fieldset>

    <button
      type="submit"
      class="primary"
      disabled={!selectedBatches}
    >
      Confirm
    </button>
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
  flex-shrink: 0;
}

button[type=submit] {
  display: block;
  margin-top: 2.5rem;
  margin-left: .9rem;
}

select {
  min-width: 12rem;
  max-width: 98%;
}

.data-type-section, .batch-selection-section, .batch-selection-section > div {
  display: flex;
}

.data-type-section, .batch-selection-section > div {
  flex-direction: column;
}

.batch-selection-section > div {
  flex-shrink: 0;
  margin-left: .5rem;
}

.batch-selection-section {
  align-items: flex-start;
  margin-bottom: 1rem;
}

.data-type-section {
  /* This prevents the checkbox labels from being clickable across all of the container's width. */
  align-items: flex-start;
}
</style>

