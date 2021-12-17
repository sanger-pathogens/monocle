<script context="module">
  // Extract `token` from the URL path and pass it to the page component as a prop.
  export function load({ page }) {
    return { props: { downloadToken: page.params.token } };
  }
</script>

<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  export let downloadToken;

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
    Your download is ready. You can close this tab once the download starts. (If you don't see a prompt to save the file, follow this <a href={downloadUrl} download>download link</a>.)
  </p>

{:else}
  <LoadingIndicator
    message="Please wait: your download is being prepared. Large downloads may take a minute or two."
  />

{/if}
