<script>
  import {
    SESSION_STORAGE_KEY_COLUMNS_STATE,
    SESSION_STORAGE_KEYS_OLD_COLUMNS_STATE,
  } from "$lib/constants.js";
  import Dialog from "$lib/components/Dialog.svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import RemoveFilterIcon from "$lib/components/icons/RemoveFilterIcon.svelte";
  import DownloadIcon from "$lib/components/icons/DownloadIcon.svelte";
  import LoadingIcon from "$lib/components/icons/LoadingIcon.svelte";
  import debounce from "$lib/utils/debounce.js";
  import { sessionStorageAvailable } from "$lib/utils/featureDetection.js";
  import {
    getBatches,
    getBulkDownloadInfo,
    getColumns,
    getInstitutions,
  } from "$lib/dataLoading.js";
  import AppMenu from "../_app-menu/index.svelte";
  import BatchSelector from "./BatchSelector.svelte";
  import BulkDownload from "./BulkDownload.svelte";
  import MetadataDownloadButton from "./MetadataDownloadButton.svelte";
  import {
    columnsStore,
    distinctColumnValuesStore,
    filterStore,
  } from "../stores.js";

  const EMPTY_STRING = "";
  const PROMISE_STATUS_REJECTED = "rejected";
  const STYLE_LOADING_ICON = "fill: lightgray";

  const dataPromise = Promise.allSettled([
    getBatches(fetch),
    getInstitutions(fetch),
    loadColumnsIntoStore(),
  ])
    .then(
      ([
        batchesSettledPromise,
        institutionsSettledPromise,
        loadColumnsIntoStorePromise,
      ]) => {
        if (batchesSettledPromise.status === PROMISE_STATUS_REJECTED) {
          console.error(
            `/get_batches rejected: ${batchesSettledPromise.reason}`
          );
          return Promise.reject(batchesSettledPromise.reason);
        }
        if (loadColumnsIntoStorePromise.status === PROMISE_STATUS_REJECTED) {
          console.error(
            `failed to load columns: ${loadColumnsIntoStorePromise.reason}.`
          );
          return Promise.reject(loadColumnsIntoStorePromise.reason);
        }
        return makeListOfBatches(
          batchesSettledPromise.value,
          institutionsSettledPromise.value
        );
      }
    )
    .catch((err) => {
      console.error(`Error while fetching batches and institutions: ${err}`);
      return Promise.reject(err);
    });

  let bulkDownloadEstimate;
  let bulkDownloadFormValues = {
    annotations: true,
    assemblies: true,
    reads: false,
  };
  let latestDownloadEstimateRequestId = 0;
  let shouldDisplayBulkDownload = false;
  let selectedBatches = null;
  let updateDownloadEstimateTimeoutId;

  $: filterStore.removeAllFilters(selectedBatches);

  $: filterActive = Object.keys($filterStore).some(
    (dataType) => Object.keys($filterStore[dataType] || []).length
  );

  $: selectedInstKeyBatchDatePairs = selectedBatches?.map(({ value }) => value);

  // These arguments are passed just to indicate to Svelte that this reactive statement
  // should re-run only when some of the arguments have changed.
  $: updateDownloadEstimate(
    selectedBatches,
    $filterStore,
    bulkDownloadFormValues
  );

  function loadColumnsIntoStore() {
    const isLocalStorageAvailable = sessionStorageAvailable();
    let locallySavedColumnsState;
    if (isLocalStorageAvailable) {
      SESSION_STORAGE_KEYS_OLD_COLUMNS_STATE.forEach((columnsStateOldKey) =>
        sessionStorage.removeItem(columnsStateOldKey)
      );
      locallySavedColumnsState = JSON.parse(
        sessionStorage.getItem(SESSION_STORAGE_KEY_COLUMNS_STATE)
      );
    }
    if (locallySavedColumnsState) {
      columnsStore.set(locallySavedColumnsState);
      return Promise.resolve();
    } else {
      return getColumns(fetch).then((columnsResponse) => {
        columnsStore.setFromColumnsResponse(columnsResponse);
        if (isLocalStorageAvailable) {
          sessionStorage.setItem(
            SESSION_STORAGE_KEY_COLUMNS_STATE,
            JSON.stringify($columnsStore)
          );
        }
      });
    }
  }

  function updateDownloadEstimate() {
    unsetDownloadEstimate();
    updateDownloadEstimateTimeoutId = debounce(
      _updateDownloadEstimate,
      updateDownloadEstimateTimeoutId
    );
  }

  function _updateDownloadEstimate() {
    const bulkDownloadFormIncomplete =
      !selectedBatches?.length ||
      (!bulkDownloadFormValues.annotations &&
        !bulkDownloadFormValues.assemblies &&
        !bulkDownloadFormValues.reads);
    if (bulkDownloadFormIncomplete) {
      return;
    }

    unsetDownloadEstimate();
    const thisRequestId = ++latestDownloadEstimateRequestId;
    getBulkDownloadInfo(
      {
        instKeyBatchDatePairs: selectedInstKeyBatchDatePairs,
        filter: {
          filterState: $filterStore,
          distinctColumnValuesState: $distinctColumnValuesStore,
        },
        ...bulkDownloadFormValues,
      },
      fetch
    )
      .then(
        ({
          num_samples,
          num_samples_restricted_to,
          size_zipped,
          size_per_zip_options = [],
        }) => {
          // Ignore stale estimates (ie estimates from requests made before the latest request for an estimate):
          if (thisRequestId === latestDownloadEstimateRequestId) {
            bulkDownloadEstimate = {
              numSamples: num_samples,
              sizeZipped: size_zipped,
              sizePerZipOptions: size_per_zip_options.map(
                ({ size_per_zip, max_samples_per_zip }) => ({
                  sizePerZip: size_per_zip,
                  maxSamplesPerZip: max_samples_per_zip,
                })
              ),
            };
            if (Number.isInteger(num_samples_restricted_to)) {
              bulkDownloadEstimate.numSamplesDownloadLimit =
                num_samples_restricted_to;
            }
          }
        }
      )
      .catch(unsetDownloadEstimate);
  }

  function unsetDownloadEstimate() {
    bulkDownloadEstimate = null;
  }

  function makeListOfBatches(batches = {}, institutions = {}) {
    return Object.keys(batches).reduce(
      (accumListOfBatches, institutionKey) =>
        addBatchListItems(
          accumListOfBatches,
          batches[institutionKey].deliveries,
          institutionKey,
          institutions[institutionKey]?.name
        ),
      []
    );
  }

  function addBatchListItems(
    accumListOfBatches,
    batches = [],
    institutionKey,
    institutionName
  ) {
    return batches.reduce((thisAccumListOfBatches, batch) => {
      thisAccumListOfBatches.push(
        makeBatchListItem(batch, institutionKey, institutionName)
      );
      return thisAccumListOfBatches;
    }, accumListOfBatches);
  }

  function makeBatchListItem(
    { name, date, number: numSamples },
    institutionKey,
    institutionName
  ) {
    const numSamplesText =
      numSamples >= 0
        ? ` (${numSamples} sample${numSamples > 1 ? "s" : EMPTY_STRING})`
        : EMPTY_STRING;
    return {
      label: `${date}: ${name}${numSamplesText}`,
      value: [institutionKey, date],
      group: institutionName || institutionKey,
    };
  }

  function removeAllFilters() {
    if (confirm("Remove all filters?")) {
      filterStore.removeAllFilters();
    }
  }
</script>

<AppMenu sampleDataLink={false} />

<h2>Sample data viewer</h2>

{#await dataPromise}
  <LoadingIndicator />
{:then batchList}
  <section class="batch-selection-section">
    <h3>Select batches</h3>
    <BatchSelector bind:selectedBatches {batchList} />
  </section>

  {#if selectedBatches?.length}
    {@const exceededSampleDownloadLimit =
      bulkDownloadEstimate?.numSamplesDownloadLimit >= 0}
    <div class="btn-group">
      <button
        aria-label="Download samples{bulkDownloadEstimate
          ? ` of size ${bulkDownloadEstimate.sizeZipped}`
          : ''}{`${exceededSampleDownloadLimit ? ' ⚠️' : EMPTY_STRING}`}"
        on:click={() => (shouldDisplayBulkDownload = true)}
        class="compact"
        type="button"
      >
        {#if bulkDownloadEstimate}
          Samples ({bulkDownloadEstimate.sizeZipped})
        {:else}
          Samples&nbsp;&nbsp;<LoadingIcon style={STYLE_LOADING_ICON} />&nbsp;
        {/if}
        <DownloadIcon />
        {#if exceededSampleDownloadLimit}
          ⚠️
        {/if}
      </button>

      <MetadataDownloadButton batches={selectedInstKeyBatchDatePairs} />

      <button
        on:click={removeAllFilters}
        class="compact remove-filters-btn"
        disabled={!filterActive ? true : null}
        type="button"
      >
        Remove all filters <RemoveFilterIcon width="24" height="17" />
      </button>
    </div>
  {/if}

  <Dialog
    bind:isOpen={shouldDisplayBulkDownload}
    ariaLabelledby="sample-bulk-download-label"
    persistState={true}
  >
    <h3 id="sample-bulk-download-label">
      Download samples
      {#if filterActive}
        <em>(filters apply)</em>
      {/if}
    </h3>
    <BulkDownload
      ariaLabelledby="sample-bulk-download-label"
      batches={selectedInstKeyBatchDatePairs}
      downloadEstimate={bulkDownloadEstimate}
      bind:formValues={bulkDownloadFormValues}
    />
  </Dialog>
{:catch}
  <p>
    An unexpected error occured during page loading. Please try again by
    reloading the page.
  </p>
{/await}

<style>
  .batch-selection-section {
    margin-bottom: 2.6rem;
    width: 100%;
  }

  .btn-group {
    margin-bottom: 0.5rem;
  }
  .btn-group button {
    margin-right: 1rem;
  }

  .remove-filters-btn {
    display: inline-flex;
    margin-left: 4rem;
  }

  em {
    font-weight: 300;
  }
</style>
