<script>
  import debounce from "$lib/utils/debounce.js"
  import { getSampleMetadata } from "$lib/dataLoading.js";
  import SampleMetadataViewerWithoutPaginaton from "./_SampleMetadataViewerWithoutPaginaton.svelte";

  export let batches;

  let sortedMetadataPromise = Promise.resolve();
  let updateMetadataTimeoutId;

  // `batches` is passed just to indicate to Svelte that this reactive statement
  // should re-run only when `batches` has changed.
  $: updateMetadata(batches);

  function updateMetadata() {
    updateMetadataTimeoutId = debounce(_updateMetadata, updateMetadataTimeoutId);
  }

  function _updateMetadata() {
    if (!batches) {
      return;
    }

    sortedMetadataPromise = getSampleMetadata(batches, fetch)
      .then((unsortedMetadata = []) => sortMetadataByOrder(unsortedMetadata));
  }

  function sortMetadataByOrder(unsortedMetadata) {
    return unsortedMetadata.map(transformSampleMetadataToSorted);
  }

  function transformSampleMetadataToSorted({ metadata }) {
    return Object.values(metadata)
      .reduce((accumSortedMetadata, metadatum) => {
        accumSortedMetadata[metadatum.order - 1] = metadatum;
        return accumSortedMetadata;
      }, []);
  }
</script>


{#if batches?.length}
  <section>
    <SampleMetadataViewerWithoutPaginaton metadataPromise={sortedMetadataPromise} />

    <nav>
      <ul>
        <li><button>First</button></li>
        <li><button>Previous</button></li>
        <li><button>Next</button></li>
        <li><button>Last</button></li>
      </ul>
    </nav>
  </section>
{/if}
