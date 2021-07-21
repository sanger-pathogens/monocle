<script>
  import DownloadIcon from "$lib/components/icons/DownloadIcon.svelte";

  export let institutionName;
  export let succeeded = 0;
  export let failed = 0;
  export let isPipeline = false;

  const PANE_TYPE = isPipeline ? "pipeline" : "sequencing";
  const URL_FAIL = encodeURI(`/download/${institutionName}/${PANE_TYPE}/failed`);
  const URL_SUCCESS = encodeURI(`/download/${institutionName}/${PANE_TYPE}/successful`);

  let titleDownloadSucceeded = isPipeline ?
    (succeeded && `Download ${succeeded} samples successfully processed through the pipeline`)
    : (succeeded && `Download ${succeeded} successfully sequenced samples`);
  let titleDownloadFailed = isPipeline ?
    (failed && `Download ${failed} samples that failed processing through the pipeline`)
    : (failed && `Download ${failed} samples that failed sequencing`);
</script>


{#if succeeded > 0}
  <a
    role="button"
    class="compact light"
    aria-label={titleDownloadSucceeded}
    title={titleDownloadSucceeded}
    href={URL_SUCCESS}
    download
    target="_blank"
    rel="external"
  >
    Download succeeded
    <DownloadIcon
      color="#98d85b"
    />
  </a>
{/if}

{#if failed > 0}
  <a
    role="button"
    class="compact light"
    aria-label={titleDownloadFailed}
    title={titleDownloadFailed}
    href={URL_FAIL}
    download
    target="_blank"
    rel="external"
  >
    Download failed
    <DownloadIcon
      color="#ff5858"
    />
  </a>
{/if}


<style>
a {
  display: inline-block;
}
</style>
