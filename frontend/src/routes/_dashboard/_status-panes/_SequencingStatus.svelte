<script>
  import DownloadButtons from "../_DownloadButtons.svelte";
  import FailMessages from "../_FailMessages.svelte";
  import StatusChart from "../_StatusChart.svelte";
  import StatusPane from "./_StatusPane.svelte";

  export let sequencingStatus = {};

  const CHART_LABELS = ["Pending", "Succeeded", "Failed"];
  const FAIL_MESSAGES_TITLE = "Sequencing Failures";

  const {
    samples_received,
    lanes_successful: succeeded,
    lanes_failed,
    samples_completed,
    fail_messages: failures,
  } = sequencingStatus;
  const pending = samples_received - samples_completed;
</script>

<StatusPane grow>
  <h3>
    {#if pending}
      <code>{samples_completed}</code> of <code>{samples_received}</code> Samples Sequenced
    {:else}
      All <code>{samples_completed}</code> Samples Sequenced
    {/if}
  </h3>

  <StatusChart labels={CHART_LABELS} values={[pending, succeeded, lanes_failed]} />

  <DownloadButtons {succeeded} />

  {#if lanes_failed > 0}
    <FailMessages {failures} title={FAIL_MESSAGES_TITLE}>
      <DownloadButtons {lanes_failed} style="float: right" />
    </FailMessages>
  {:else}
    <FailMessages {failures} title={FAIL_MESSAGES_TITLE} />
  {/if}
</StatusPane>
