<script>
  import { DATA_TYPES } from "$lib/constants.js";
  import debounce from "$lib/utils/debounce.js";
  import { getSampleMetadata } from "$lib/dataLoading.js";
  import {
    displayedColumnNamesStore,
    distinctColumnValuesStore,
    filterStore,
  } from "../../_stores.js";
  import PaginationNav from "./_PaginationNav.svelte";
  import SampleMetadataViewerWithoutPaginaton from "./_SampleMetadataViewerWithoutPaginaton.svelte";

  export let batches = undefined;

  const MAX_METADATA_FETCH_FREQUENCY_MS = 800;
  const NUM_METADATA_ROWS_PER_PAGE = 17;

  let initialLoading = true;
  let metadataTimeoutId;
  let numSamples;
  let requestedPageNum = 1;
  let displayedPageNum = requestedPageNum;
  let sortedMetadataPromise;

  // These arguments are passed just to indicate to Svelte that this reactive statement
  // should re-run only when one of the arguments has changed.
  $: resetPageNum(batches, $displayedColumnNamesStore, $filterStore);
  $: updateMetadata(
    batches,
    $displayedColumnNamesStore,
    $filterStore,
    requestedPageNum
  );

  function updateMetadata() {
    showMetadataLoading();
    metadataTimeoutId = debounce(
      _updateMetadata,
      metadataTimeoutId,
      MAX_METADATA_FETCH_FREQUENCY_MS
    );
    preventDebouncingFirstMetadataRequest();
  }

  function _updateMetadata() {
    if (!batches) {
      return;
    }

    // FIXME: prevent duplicate request when a batch is selected for the first time.
    sortedMetadataPromise = getSampleMetadata(
      {
        instKeyBatchDatePairs: batches,
        filter: {
          filterState: $filterStore,
          distinctColumnValuesState: $distinctColumnValuesStore,
        },
        columns: $displayedColumnNamesStore,
        numRows: NUM_METADATA_ROWS_PER_PAGE,
        startRow: NUM_METADATA_ROWS_PER_PAGE * (requestedPageNum - 1) + 1,
      },
      fetch
    ).then((metadataResponse = {}) => {
      const sortedMetadata = sortMetadataByOrder(metadataResponse.samples);
      numSamples = metadataResponse["total rows"];
      displayedPageNum = requestedPageNum;
      initialLoading = false;
      return sortedMetadata;
    });
  }

  function sortMetadataByOrder(unsortedMetadata = []) {
    return unsortedMetadata.map(transformSampleMetadataToSorted);
  }

  function transformSampleMetadataToSorted(sampleMetadata) {
    return DATA_TYPES.reduce((accumSampleMetadata, dataType) => {
      Object.keys(sampleMetadata[dataType] || {})
        .map((columnName) => {
          const column = sampleMetadata[dataType][columnName];
          column.name = columnName;
          column.dataType = dataType;
          return column;
        })
        .sort(compareMetadataByOrder)
        .forEach((sampleMetadataParam) =>
          accumSampleMetadata.push(sampleMetadataParam)
        );
      return accumSampleMetadata;
    }, []);
  }

  function compareMetadataByOrder(metadatumA, metadatumB) {
    return metadatumA.order - metadatumB.order;
  }

  function onPageChange(event) {
    const pageNumCandidate = Math.max(event.detail, 1);
    if (pageNumCandidate !== displayedPageNum) {
      requestedPageNum = pageNumCandidate;
    }
  }

  function resetPageNum() {
    requestedPageNum = 1;
    numSamples = undefined;
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
</script>

{#if batches?.length}
  <section>
    {#if !initialLoading}
      <PaginationNav
        compact={true}
        {numSamples}
        maxNumSamplesPerPage={NUM_METADATA_ROWS_PER_PAGE}
        pageNum={displayedPageNum}
        on:pageChange={onPageChange}
      />
    {/if}

    <SampleMetadataViewerWithoutPaginaton
      {batches}
      metadataPromise={sortedMetadataPromise}
    />

    <PaginationNav
      {numSamples}
      maxNumSamplesPerPage={NUM_METADATA_ROWS_PER_PAGE}
      pageNum={displayedPageNum}
      on:pageChange={onPageChange}
    />
  </section>
{/if}

<style>
  section {
    max-width: 100%;
  }
</style>
