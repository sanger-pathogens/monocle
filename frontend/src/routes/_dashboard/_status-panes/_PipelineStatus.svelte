<script>
  import DownloadButtons from "../_DownloadButtons.svelte";
  import FailMessages from "../_FailMessages.svelte";
  import StatusPane from "./_StatusPane.svelte";
  import StatusChart from "../_StatusChart.svelte";

  export let pipelineStatus = {};

  const CHART_LABELS = ["Pending", "Succeeded", "Failed"];
  const FAIL_MESSAGES_TITLE = "Pipeline Failures";

  const {
    sequencedSuccess,
    success: succeeded,
    failed,
    completed,
    fail_messages: failures,
  } = pipelineStatus;
  const pending = sequencedSuccess - completed;
</script>

<StatusPane grow>
  {#if sequencedSuccess === 0}
    <h3>No Pipelines Started</h3>
  {:else}
    <h3>
      {#if pending > 0}
        <code>{completed}</code> of <code>{sequencedSuccess}</code> Pipelines Completed
      {:else}
        All <code>{completed}</code> Pipelines Completed
      {/if}
    </h3>

    <StatusChart labels={CHART_LABELS} values={[pending, succeeded, failed]} />

    <DownloadButtons {succeeded} isPipeline={true} />

    {#if failed > 0}
      <FailMessages {failures} title={FAIL_MESSAGES_TITLE}>
        <DownloadButtons {failed} isPipeline={true} style="float: right" />
      </FailMessages>
    {:else}
      <FailMessages {failures} title={FAIL_MESSAGES_TITLE} />
    {/if}
  {/if}
</StatusPane>
