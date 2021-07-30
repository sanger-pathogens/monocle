<script>
  import DownloadButtons from "../_DownloadButtons.svelte";
  import FailMessages from "../_FailMessages.svelte";
  import StatusChart from "../_StatusChart.svelte";
  import StatusPane from "./_StatusPane.svelte";

  export let sequencingStatus = {};

  const CHART_LABELS = ["Pending", "Succeeded", "Failed"];
  const FAIL_MESSAGES_TITLE = "Sequencing Failures";
  
  const { received, success: succeeded, failed, completed, fail_messages: failures } =
    sequencingStatus;
  const pending = received - completed;
</script>


<StatusPane grow>
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

  <DownloadButtons {succeeded} />

  {#if failed > 0}
    <FailMessages
      {failures}
      title={FAIL_MESSAGES_TITLE}
    >
      <DownloadButtons {failed} style="float: right" />
    </FailMessages>
  {:else}
    <FailMessages
      {failures}
      title={FAIL_MESSAGES_TITLE}
    />
  {/if}
</StatusPane>

