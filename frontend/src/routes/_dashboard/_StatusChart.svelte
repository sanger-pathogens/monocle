<script>
  import SlicedChart from '$lib/components/SlicedChart.svelte';

  export let labels = [];
  export let values = [];

  const CHART_TITLE =
    // `+` in front is needed to convert a string to a number,
    // which is done to truncate trailing decimal zeros.
    `${+(calcPercentCompleted(values) * 100).toFixed(1)}% completed`;
  const SEGMENT_COLORS = ["light-grey", "light-green", "red"];

  function calcPercentCompleted(values) {
    const [pending, succeeded, failed] = values;
    const completed = succeeded + failed;
    const received = completed + pending;
    return received ? completed / received : 0;
  }
</script>


<SlicedChart
  title={CHART_TITLE}
  {labels}
  {values}
  colors={SEGMENT_COLORS}
/>
