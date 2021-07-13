<script>
  import Card from "$lib/components/Card.svelte";
  import Dialog from "$lib/components/Dialog.svelte";
  import StatusChart from "./_StatusChart.svelte";

  export let sequencingStatus = {};

  const CHART_LABELS = ["Pending", "Succeeded", "Failed"];
  
  const { received, success: succeeded, failed, completed, fail_messages: failures } =
    sequencingStatus;
  const pending = received - completed;
  const hasFailMessages = failures?.length;
  let dialogOpen;
</script>


<Card>
  <h4>
    {#if pending}
      <code>{completed}</code> of <code>{received}</code> Samples Sequenced
    {:else}
      All <code>{completed}</code> Samples Sequenced
    {/if}
  </h4>

  <StatusChart
    labels={CHART_LABELS}
    values={[pending, succeeded, failed]}
  />
  <!-- FIXME: extract into component -->
  {#if hasFailMessages}
    <button on:click={() => dialogOpen = true} class="light">
      Show fail messages
    </button>

    <Dialog bind:isOpen={dialogOpen}>
      <h4>Sequencing Failures</h4>
      <table>
        <tr>
          <th>lane</th>
          <th>stage</th>
          <th class="fail-msg-column">fail message</th>
        </tr>
        {#each failures as { lane, stage, issue } (lane+stage+issue)}
          <tr>
            <td>{lane}</td>
            <td>{stage}</td>
            <td>{issue}</td>
          </tr>
        {/each}
      </table>
    </Dialog>
  {/if}
</Card>


<style>
button {
  display: block;
  margin: .9rem 0 0;
}

.fail-msg-column {
  width: 48%;
}
</style>

