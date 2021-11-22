<script>
  import debounce from "$lib/utils/debounce.js"
  import { getSampleMetadata } from "$lib/dataLoading.js";
  import SampleMetadataViewerWithoutPaginaton from "./_SampleMetadataViewerWithoutPaginaton.svelte";

  export let batches = undefined;

  const NUM_METADATA_ROWS_PER_PAGE = 12;

  let sortedMetadataPromise;
  let updateMetadataTimeoutId;

  // `batches` is passed just to indicate to Svelte that this reactive statement
  // should re-run only when `batches` has changed.
  $: updateMetadata(batches);

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
      numRows: NUM_METADATA_ROWS_PER_PAGE
    }, fetch)
      .then((unsortedMetadata = []) => sortMetadataByOrder(unsortedMetadata));
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
</script>


{#if batches?.length}
  <section>
    <SampleMetadataViewerWithoutPaginaton metadataPromise={sortedMetadataPromise} />

    <nav>
      <ul>
        <!-- `type="button"` is needed to prevent the buttons from submitting a form that they
          may be a descendant of. -->
        <li><button type="button">First</button></li>
        <li><button type="button">Previous</button></li>
        <li><button type="button">Next</button></li>
        <li><button type="button">Last</button></li>
      </ul>
    </nav>
  </section>
{/if}
