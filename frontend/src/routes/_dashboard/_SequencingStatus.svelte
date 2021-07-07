<script>
  import Card from "$lib/components/Card.svelte";
  import StatusChart from "./_StatusChart.svelte";

  export let sequencingStatus = {};

  const CHART_LABELS = ["Pending", "Succeeded", "Failed"];
  
  const { received, success: succeeded, failed, completed } =
    sequencingStatus;
  const pending = received - completed;
</script>


<Card style="order: 1">
  <h4>
    {#if completed < received}
      <code>{completed}</code> of <code>{received}</code> Samples Sequenced
    {:else}
      All <code>{completed}</code> Samples Sequenced
    {/if}
  </h4>

  <StatusChart
    labels={CHART_LABELS}
    values={[pending, succeeded, failed]}
  />
</Card>

