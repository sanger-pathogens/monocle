<script>
  import SlicedChart from "$lib/components/SlicedChart.svelte";

  export let labels = [];
  export let values = [];
  export let includesRunning = false;

  const CHART_TITLE =
    // `+` in front is needed to convert a string to a number,
    // which is done to truncate trailing decimal zeros.
    `${+(calcPercentCompleted(values) * 100).toFixed(1)}% completed`;
  const SEGMENT_COLORS = includesRunning ?
    ["light-grey", "light-blue", "light-green", "red"]
    : ["light-grey", "light-green", "red"];

  function calcPercentCompleted(values) {
    let pending, running = 0, succeeded, failed;
    if (includesRunning) {
      [pending, running, succeeded, failed] = values;
    }
    else {
      [pending, succeeded, failed] = values;
    }
    const completed = succeeded + failed;
    const received = completed + pending + running;
    return received ? completed / received : 0;
  }
</script>


<SlicedChart
  title={CHART_TITLE}
  {labels}
  {values}
  colors={SEGMENT_COLORS}
/>

