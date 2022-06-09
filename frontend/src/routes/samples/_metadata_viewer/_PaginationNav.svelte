<script context="module">
  export const EVENT_NAME_PAGE_CHANGE = "pageChange";
</script>

<script>
  import { createEventDispatcher } from "svelte";

  export let compact = false;
  export let numSamples = undefined;
  export let maxNumSamplesPerPage;
  export let pageNum;

  const dispatch = createEventDispatcher();

  $: isLastPage = maxNumSamplesPerPage * pageNum >= numSamples;
  $: lastSampleNum = Math.min(maxNumSamplesPerPage * pageNum, numSamples);
  $: firstSampleNum = maxNumSamplesPerPage * (pageNum - 1) + 1;
</script>

<nav>
  <ul class:compact>
    <!-- TODO: cache metadata so as to avoid waiting when one of the buttons is clicked. -->
    <!-- `type="button"` is needed to prevent the buttons from submitting a form that they
      may be a descendant of. -->
    <li>
      <button
        aria-label="First page"
        class="compact"
        type="button"
        on:click={() => dispatch(EVENT_NAME_PAGE_CHANGE, 1)}
        disabled={pageNum <= 1}
      >
        &lt&lt First
      </button>
    </li>

    <li>
      <button
        aria-label="Previous page"
        class="compact"
        type="button"
        on:click={() =>
          dispatch(EVENT_NAME_PAGE_CHANGE, Math.max(pageNum - 1, 1))}
        disabled={pageNum <= 1}
      >
        &lt Previous
      </button>
    </li>

    <li
      aria-hidden={!numSamples ? "true" : null}
      aria-label={numSamples
        ? `displaying samples from ${firstSampleNum} to ${lastSampleNum} out of ${numSamples}`
        : null}
      class="num-samples"
    >
      {#if numSamples}
        <code>{firstSampleNum}-{lastSampleNum}</code> of
        <code>{numSamples}</code>
        <div>samples</div>
      {/if}
    </li>

    <li>
      <button
        aria-label="Next page"
        class="compact"
        type="button"
        on:click={() => dispatch(EVENT_NAME_PAGE_CHANGE, pageNum + 1)}
        disabled={isLastPage}
      >
        Next &gt
      </button>
    </li>
  </ul>
</nav>

<style>
  ul {
    display: flex;
    justify-content: center;
    list-style: none;
    padding-left: 0;
    padding-right: 3rem;
  }

  li {
    margin-left: 1rem;
  }

  ul.compact {
    margin: 1.4rem 0 0.2rem;
  }
  .compact .num-samples {
    margin-left: 0.2rem;
    margin-top: 0.2rem;
  }
  .compact .num-samples + li {
    margin-left: 0.6rem;
  }
  .compact button {
    font-size: 0.8rem;
    padding: 0.4rem;
  }

  .num-samples,
  .num-samples code {
    color: var(--text-muted);
    font-size: 0.75rem;
  }
  .num-samples {
    margin-left: 0.8rem;
    margin-top: 0.3rem;
    min-width: 2.3rem;
  }
  .num-samples div {
    line-height: 0.8;
    text-align: center;
  }
</style>
