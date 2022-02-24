<script>
  import debounce from "$lib/utils/debounce.js";
  import { getSampleMetadata } from "$lib/dataLoading.js";
  import { columnsToDisplayStore, distinctColumnValuesStore, filterStore } from "../_stores.js";
  import SampleMetadataViewerWithoutPaginaton from "./_SampleMetadataViewerWithoutPaginaton.svelte";

  export let batches = undefined;

  const MAX_METADATA_FETCH_FREQUENCY_MS = 800;
  const NUM_METADATA_ROWS_PER_PAGE = 16;

  let isLastPage = false;
  let pageNum = 1;
  let sortedMetadataPromise;
  let metadataTimeoutId;

  // `batches` is passed just to indicate to Svelte that this reactive statement
  // should re-run only when `batches` has changed.
  $: setToFirstPage(batches);
  // FIXME unit test request being made on columns change
  $: updateMetadata(batches, pageNum, $columnsToDisplayStore, $filterStore);

  function updateMetadata() {
    showMetadataLoading();
    metadataTimeoutId = debounce(_updateMetadata, metadataTimeoutId, MAX_METADATA_FETCH_FREQUENCY_MS);
    preventDebouncingFirstMetadataRequest();
  }

  function _updateMetadata() {
    if (!batches) {
      return;
    }

    // FIXME: prevent duplicate request when a batch is selected for the first time.
    sortedMetadataPromise = getSampleMetadata({
      instKeyBatchDatePairs: batches,
      filter: { filterState: $filterStore, distinctColumnValues: $distinctColumnValuesStore },
      columns: $columnsToDisplayStore,
      numRows: NUM_METADATA_ROWS_PER_PAGE,
      startRow: NUM_METADATA_ROWS_PER_PAGE * (pageNum - 1) + 1
    }, fetch)
      .then((metadataResponse = {}) => {
        const sortedMetadata = sortMetadataByOrder(metadataResponse.samples);
        isLastPage = metadataResponse["last row"] >= metadataResponse["total rows"];
        return sortedMetadata;
      });
  }

  function sortMetadataByOrder(unsortedMetadata = []) {
    return unsortedMetadata.map(transformSampleMetadataToSorted);
  }

  function transformSampleMetadataToSorted({ metadata }) {
    return { metadata: Object.keys(metadata)
      .map((columnName) => {
        metadata[columnName].name = columnName;
        return metadata[columnName];
      })
      .sort(compareMetadataByOrder)
    };
  }

  function compareMetadataByOrder(metadatumA, metadatumB) {
    return metadatumA.order - metadatumB.order;
  }

  function preventDebouncingFirstMetadataRequest() {
    setTimeout(resetMetadataTimeoutId, MAX_METADATA_FETCH_FREQUENCY_MS);
  }

  function resetMetadataTimeoutId() {
    metadataTimeoutId = null;
  }

  function showMetadataLoading() {
    sortedMetadataPromise = new Promise(() => {});
  }

  function incrementPage() {
    pageNum += 1;
  }

  function decrementPage() {
    if (pageNum > 1) {
      pageNum -= 1;
    }
    // Never say "never"?
    else if (pageNum < 1) {
      setToFirstPage();
    }
  }

  function setToFirstPage() {
    pageNum = 1;
  }
</script>


{#if batches?.length}
  <section>

    <SampleMetadataViewerWithoutPaginaton metadataPromise={sortedMetadataPromise} />

    <nav>
      <ul>
        <!-- TODO: cache metadata so as to avoid waiting when one of the buttons is clicked. -->
        <!-- `type="button"` is needed to prevent the buttons from submitting a form that they
          may be a descendant of. -->
        <li><button
          aria-label="First page"
          class="compact"
          type="button"
          on:click={setToFirstPage}
          disabled={pageNum <= 1}
        >
          &lt&lt First
        </button></li>
        <li><button
          aria-label="Previous page"
          class="compact"
          type="button"
          on:click={decrementPage}
          disabled={pageNum <= 1}
        >
          &lt Previous
        </button></li>
        <li><button
          aria-label="Next page"
          class="compact"
          type="button"
          on:click={incrementPage}
          disabled={isLastPage}
        >
          Next &gt
        </button></li>
      </ul>
    </nav>
  </section>
{/if}


<style>
section {
  position: relative;
  width: 100%;
  max-width: 100%;
}

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
</style>
