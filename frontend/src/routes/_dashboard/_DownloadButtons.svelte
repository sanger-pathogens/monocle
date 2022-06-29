<script>
  import { getContext } from "svelte";
  import DownloadIcon from "$lib/components/icons/DownloadIcon.svelte";

  export let succeeded = 0;
  export let failed = 0;
  export let isPipeline = false;
  export let style = "";

  const INSTITUTION_NAME = getContext("institutionName");
  const PANE_TYPE = isPipeline ? "pipeline" : "sequencing";
  const URL_FAIL = encodeURI(
    `/download/${INSTITUTION_NAME}/${PANE_TYPE}/failed`
  );
  const URL_SUCCESS = encodeURI(
    `/download/${INSTITUTION_NAME}/${PANE_TYPE}/successful`
  );

  const onlyFailedButton = !succeeded;
  const titleDownloadSucceeded = isPipeline
    ? succeeded &&
      `Download metadata for ${succeeded} samples successfully processed through the pipeline`
    : succeeded &&
      `Download metadata for ${succeeded} successfully sequenced samples`;
  const titleDownloadFailed = isPipeline
    ? failed &&
      `Download metadata for ${failed} samples that failed processing through the pipeline`
    : failed &&
      `Download metadata for ${failed} samples that failed sequencing`;
</script>

{#if !onlyFailedButton}
  <a
    role="button"
    class="compact"
    aria-label={titleDownloadSucceeded}
    title={titleDownloadSucceeded}
    href={URL_SUCCESS}
    download
    target="_blank"
    rel="external"
    {style}
  >
    Metadata for successful samples
    <DownloadIcon color="#98d85b" />
  </a>
{/if}

{#if failed > 0}
  <a
    role="button"
    class:compact={!onlyFailedButton}
    aria-label={titleDownloadFailed}
    title={titleDownloadFailed}
    href={URL_FAIL}
    download
    target="_blank"
    rel="external"
    {style}
  >
    {onlyFailedButton ? "Download" : "Metadata for failed samples"}
    <DownloadIcon color="#ff5858" />
  </a>
{/if}

<style>
  a {
    display: inline-block;
  }
</style>
