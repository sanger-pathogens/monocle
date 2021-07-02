<script>
  import { onMount } from "svelte";
  import { Chart } from "frappe-charts";

  export let datasets = [];
  export let height = 320;
  export let labels = [];
  export let title;

  const chartOptions = {
    title,
    type: "line",
    height,
    axisOptions: {
      xIsSeries: true
    },
    lineOptions: {
      hideDots: 1
    },
    data: {
      labels,
      datasets
    }
  };
  let chartElement;

  onMount(() => {
    new Chart(chartElement, chartOptions);
  });
</script>


<div bind:this={chartElement}></div>


<style>
/* TODO: is there a way to style dynamic elements w/o "polluting" global CSS? */
:global(.frappe-chart .title) {
  font-size: 1rem;
}
</style>

