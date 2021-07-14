<script>
  import { onMount } from "svelte";
  import { Chart } from "frappe-charts";

  export let title;
  // Other sliced types are "percentage" and "pie"
  // (https://frappe.io/charts/docs/basic/aggr_sliced_diags).
  export let type = "donut";
  export let labels = [];
  export let values = [];
  export let colors = undefined;
  export let height = undefined;

  const chartOptions = {
    title,
    type,
    // If `colors` is truthy, add `colors` property to the options w/ the spread operator.
    ...(colors && { colors }),
    ...(height && { height }),
    animate: false,
    data: {
      labels,
      datasets: [{ values }]
    }
  };
  let chartElement;

  onMount(() => {
    new Chart(chartElement, chartOptions);
  });
</script>


<div bind:this={chartElement}></div>


<style>
</style>

