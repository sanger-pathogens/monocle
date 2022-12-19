<script>
  import { setContext } from "svelte";
  import BatchStatus from "./status-panes/BatchStatus.svelte";
  import SequencingStatus from "./status-panes/SequencingStatus.svelte";
  import PipelineStatus from "./status-panes/PipelineStatus.svelte";

  export let institutionKey;
  export let institutionName;
  export let batches;
  export let sequencingStatus;
  export let pipelineStatus;

  const apiError =
    batches._ERROR || sequencingStatus._ERROR || pipelineStatus._ERROR;

  // Svelte's context is like a store but available only to a component and its descendants.
  setContext("institutionKey", institutionKey);
</script>

<article>
  <h2>{institutionName}</h2>

  {#if apiError}
    <p>⚠️ {apiError}</p>
  {:else if batches.received}
    <BatchStatus {batches} />
    <SequencingStatus {sequencingStatus} />
    <PipelineStatus {pipelineStatus} />
  {:else}
    <p>No samples received</p>
  {/if}
</article>

<style>
  article {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-evenly;
  }

  article:not(:first-of-type) {
    margin-top: 3.2rem;
  }
  article:first-of-type {
    margin-top: 1.5rem;
  }

  h2 {
    margin-top: 1rem;
    width: 100%;
  }

  p {
    text-align: center;
  }
</style>
