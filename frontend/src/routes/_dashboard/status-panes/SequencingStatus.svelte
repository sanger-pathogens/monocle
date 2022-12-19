<script>
  import DownloadButtons from "../DownloadButtons.svelte";
  import FailMessages from "../FailMessages.svelte";
  import StatusChart from "../StatusChart.svelte";
  import StatusPane from "./StatusPane.svelte";

  export let sequencingStatus = {};

  const CHART_LABELS = ["Pending", "Successful runs", "Failed runs"];
  const FAIL_MESSAGES_TITLE = "Sequencing Failures";

  const {
    samples_received: samplesReceived,
    lanes_successful: lanesSuccessful,
    lanes_failed: lanesFailed,
    samples_completed: samplesCompleted,
    fail_messages: failures,
  } = sequencingStatus;
  const pending = samplesReceived - samplesCompleted;
</script>

<StatusPane grow>
  <h3>
    {#if pending}
      <code>{samplesCompleted}</code> of <code>{samplesReceived}</code> Samples Sequenced
    {:else}
      All <code>{samplesCompleted}</code> Samples Sequenced
    {/if}
  </h3>

  <StatusChart
    labels={CHART_LABELS}
    values={[pending, lanesSuccessful, lanesFailed]}
  />

  <DownloadButtons succeeded={lanesSuccessful} />

  {#if lanesFailed > 0}
    <FailMessages {failures} title={FAIL_MESSAGES_TITLE}>
      <DownloadButtons failed={lanesFailed} style="float: right" />
    </FailMessages>
  {:else}
    <FailMessages {failures} title={FAIL_MESSAGES_TITLE} />
  {/if}
</StatusPane>
