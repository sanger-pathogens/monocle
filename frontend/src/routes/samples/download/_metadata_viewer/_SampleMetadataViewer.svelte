<script>
  import debounce from "$lib/utils/debounce.js"
  import { getSampleMetadata } from "$lib/dataLoading.js";
  import SampleMetadataViewerWithoutPaginaton from "./_SampleMetadataViewerWithoutPaginaton.svelte";

  export let batches = undefined;

  const NUM_METADATA_ROWS_PER_PAGE = 12;

  // This var is used to detect the last page.
  let numMetadataRowsDisplayed = 0;
  let pageNum = 1;
  let sortedMetadataPromise;
  let updateMetadataTimeoutId;

  // `batches` is passed just to indicate to Svelte that this reactive statement
  // should re-run only when `batches` has changed.
  $: setToFirstPage(batches);
  $: updateMetadata(batches, pageNum);

  function updateMetadata() {
    showMetadataLoading();
    updateMetadataTimeoutId = debounce(_updateMetadata, updateMetadataTimeoutId);
  }

  function _updateMetadata() {
    if (!batches) {
      hideMetadataLoading();
      return;
    }

    sortedMetadataPromise = getSampleMetadata({
      instKeyBatchDatePairs: batches,
      numRows: NUM_METADATA_ROWS_PER_PAGE,
      startRow: NUM_METADATA_ROWS_PER_PAGE * (pageNum - 1) + 1
    }, fetch)
      .then((unsortedMetadata = []) => {
        const sortedMetadata = sortMetadataByOrder(unsortedMetadata);
        numMetadataRowsDisplayed = sortedMetadata.length;
        return sortedMetadata;
      });
  }

  function sortMetadataByOrder(unsortedMetadata) {
    return unsortedMetadata.map(transformSampleMetadataToSorted);
  }

  function transformSampleMetadataToSorted({ metadata }) {
    return { metadata: Object.values(metadata)
      .sort(compareMetadataByOrder)
    };
  }

  function compareMetadataByOrder(metadatumA, metadatumB) {
    return metadatumA.order - metadatumB.order;
  }

  function showMetadataLoading() {
    sortedMetadataPromise = new Promise(() => {});
  }

  function hideMetadataLoading() {
    sortedMetadataPromise = null;
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

  function isLastPage() {
    return numMetadataRowsDisplayed < NUM_METADATA_ROWS_PER_PAGE;
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
        <li><button type="button" on:click={setToFirstPage} disabled={pageNum <= 1}>
          First
        </button></li>
        <li><button type="button" on:click={incrementPage} disabled={pageNum <= 1}>
          Previous
        </button></li>
        <li><button type="button" on:click={decrementPage} disabled={isLastPage()}>
          Next
        </button></li>
      </ul>
    </nav>
  </section>
{/if}
