<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  const downloadToken = window.location.pathname.split("/").pop();
  const downloadUrl = `/data_download/${downloadToken}`
  let downloadPrepared = false;

  function beforeDownload() {
    downloadPrepared = true;
  }
</script>


<svelte:head>
  <meta http-equiv="refresh" content="0; url={downloadUrl}" />
</svelte:head>

<svelte:window on:beforeunload={beforeDownload} />

{#if downloadPrepared}
  <p>
    Your download is ready. (If you don't see a prompt to save the file, follow this <a href={downloadUrl} download>link</a>.)
  </p>

{:else}
  <LoadingIndicator
    message="Please wait: your download is being prepared. Large downloads may take a minute or two."
  />

{/if}
