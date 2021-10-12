<script>
  import DownloadIcon from "$lib/components/icons/DownloadIcon.svelte";
  import DownloadButtons from "../_DownloadButtons.svelte";
  import FailMessages from "../_FailMessages.svelte";
  import StatusPane from "./_StatusPane.svelte";
  import StatusChart from "../_StatusChart.svelte";

  export let pipelineStatus = {};

  const CHART_LABELS = ["Waiting", "Running", "Succeeded", "Failed"];
  const FAIL_MESSAGES_TITLE = "Pipeline Failures";
  const LABEL_BULK_DOWNLOAD = "Bulk data download";

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


<StatusPane grow>
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

    <DownloadButtons
      {succeeded}
      isPipeline={true}
    />

    {#if failed > 0}
      <FailMessages
        {failures}
        title={FAIL_MESSAGES_TITLE}
      >
        <DownloadButtons
          {failed}
          isPipeline={true}
          style="float: right"
        />
      </FailMessages>
    {:else}
      <FailMessages
        {failures}
        title={FAIL_MESSAGES_TITLE}
      />
    {/if}

    <a
      href="/samples/download"
      aria-label={LABEL_BULK_DOWNLOAD}
      title={LABEL_BULK_DOWNLOAD}
    >
      Bulk data <DownloadIcon color="var(--text-muted)" />
    </a>
  {/if}
</StatusPane>

<style>
a {
  color: var(--form-text);
  font-weight: 100;
  white-space: nowrap;
}
</style>
