<script>
  import Card from "$lib/components/Card.svelte";
  import FailMessages from "./_FailMessages.svelte";
  import StatusChart from "./_StatusChart.svelte";

  export let pipelineStatus = {};

  const CHART_LABELS = ["Waiting", "Running", "Succeeded", "Failed"];
  const FAIL_MESSAGES_TITLE = "Pipeline Failures";

  const {
    sequencedSuccess,
    running,
    success: succeeded,
    failed,
    completed,
    fail_messages: failures
  } = pipelineStatus;
  const waiting = sequencedSuccess - completed;
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
  
    <FailMessages
      {failures}
      title={FAIL_MESSAGES_TITLE}
    />
  {/if}
</Card>

