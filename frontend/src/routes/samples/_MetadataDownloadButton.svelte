<script>
  import DownloadIcon from "$lib/components/icons/DownloadIcon.svelte";
  import LoadingIcon from "$lib/components/icons/LoadingIcon.svelte";
  import { getSampleMetadata } from "$lib/dataLoading.js";
  import { distinctColumnValuesStore, filterStore } from "./_stores.js";

  export let batches;
  export let fileNameWithoutExtension = "monocle-metadata";
  export let filterState = undefined;
  export let distinctColumnValuesState = undefined;
  export let style = undefined;
  export let injectedCreateAnchorElement = undefined;

  let isPreparingDownload = false;

  function downloadMetadata() {
    if (!batches?.length) {
      return;
    }

    isPreparingDownload = true;

    let csvBlobUrl;
    let hiddenDownloadLink;
    getSampleMetadata({
      instKeyBatchDatePairs: batches,
      filter: {
        filterState: filterState || $filterStore,
        distinctColumnValuesState: distinctColumnValuesState || $distinctColumnValuesStore
      },
      asCsv: true
    }, fetch)
      .then((csvBlob) => {
        csvBlobUrl = URL.createObjectURL(csvBlob);
        hiddenDownloadLink = document.body.appendChild(
          createHiddenDownloadLink(csvBlobUrl, `${fileNameWithoutExtension}.csv`));
        hiddenDownloadLink.click();
      })
      .catch((err) => console.error(`Error on creating metadata download: ${err}`))
      .finally(() => {
        isPreparingDownload = false;
        hiddenDownloadLink && document.body.removeChild(hiddenDownloadLink);
        URL.revokeObjectURL(csvBlobUrl);
      });
  }

  function createHiddenDownloadLink(url, fileName) {
    const a = injectedCreateAnchorElement?.() || document.createElement("a");
    a.style = "display: none";
    a.href = url;
    a.download = fileName;
    return a;
  }
</script>


<button
  aria-label={isPreparingDownload ? null : "Download metadata"}
  on:click={downloadMetadata}
  class="compact"
  type="button"
  disabled={isPreparingDownload}
  {style}
>
  {#if isPreparingDownload}
    Preparing download <LoadingIcon />
  {:else}
    Metadata <DownloadIcon />
  {/if}
</button>
