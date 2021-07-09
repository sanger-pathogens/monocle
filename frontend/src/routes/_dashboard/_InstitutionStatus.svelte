<script>
  import BatchStatus from "./_BatchStatus.svelte";
  import SequencingStatus from "./_SequencingStatus.svelte";

  export let institutionName;
  export let batches;
  export let sequencingStatus;
</script>


<article>
  <h3>{institutionName}</h3>

  {#if batches.received}
    <BatchStatus {batches} />
    <SequencingStatus {sequencingStatus} />
  {:else}
    <p>No samples received</p>
  {/if}

</article>


<style>
:root {
  --width-main: min(98vw, var(--bp-xl));
}

article {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

article:not(:first-of-type) {
  margin-top: 3.4rem;
}
article:first-of-type {
  margin-top: 1.5rem;
}

h3 {
  margin-top: 1rem;
  width: 100%;
}

p {
  text-align: center;
}
</style>
