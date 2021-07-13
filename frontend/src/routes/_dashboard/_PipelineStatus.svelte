<script>
  import Card from "$lib/components/Card.svelte";
  import Dialog from "$lib/components/Dialog.svelte";
  import StatusChart from "./_StatusChart.svelte";

  export let pipelineStatus = {};

  const CHART_LABELS = ["Waiting", "Running", "Succeeded", "Failed"];
  
  const {
    sequencedSuccess,
    running,
    success: succeeded,
    failed,
    completed,
    fail_messages: failures
  } = pipelineStatus;
  const waiting = sequencedSuccess - completed;
  const hasFailMessages = failures?.length;
  let dialogOpen;
</script>


<Card>
  {#if sequencedSuccess === 0}
    <h4>
      No Pipelines Started
    </h4>
  {:else}
    <h4>
      {#if waiting > 0}
        <code>{completed}</code> of <code>{sequencedSuccess}</code> Sample Pipelines Completed
      {:else}
        All <code>{completed}</code> Sample Pipelines Completed
      {/if}
    </h4>
  
    <StatusChart
      labels={CHART_LABELS}
      values={[waiting, running, succeeded, failed]}
      includesRunning={true}
    />
  
    {#if hasFailMessages}
      <button on:click={() => dialogOpen = true} class="light">
        Show fail messages
      </button>
  
      <Dialog bind:isOpen={dialogOpen}>
        <h4>Pipeline Failures</h4>
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

