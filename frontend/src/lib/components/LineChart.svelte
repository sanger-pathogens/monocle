<script>
  import { onMount } from "svelte";
  import { Chart } from "frappe-charts";

  export let datasets = [];
  export let height = 320;
  export let xLabels = [];
  export let yLabel = "";
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
      labels: xLabels,
      datasets
    }
  };
  let chartElement;

  onMount(() => {
    new Chart(chartElement, chartOptions);
  });
</script>


<div aria-label="project progress chart: number fo samples over time" class="container">
  <div
    bind:this={chartElement}
    style="--initial-height: {height}px"
  ></div>
  <!-- TODO: replace w/ Frappe Charts' own implementation of Y label once it makes
  it to the library (see eg this issue: https://github.com/frappe/charts/issues/219) -->
  {#if yLabel}
    <div class="y-label" aria-hidden="true">
      {yLabel}
    </div>
  {/if}
</div>


<style>
/* TODO: is there a way to style dynamic elements w/o "polluting" global CSS? */
:global(.frappe-chart .title) {
  font-size: 1rem;
}

.container {
  position: relative;
  margin: 0 auto;
  min-height: var(--initial-height);
  width: var(--width-reading);
  max-width: 100%;
}

.y-label {
  position: absolute;
  transform: rotate(-90deg) translate(225%, -200%);
  color: var(--text-muted);
  font-size: .8rem;
  font-weight: 300;
}
</style>

