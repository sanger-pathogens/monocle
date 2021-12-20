<script context="module">
  // Extract `token` from the URL path and pass it to the page component as a prop.
  export function load({ page }) {
    return { props: { downloadToken: page.params.token } };
  }
</script>

<script>
  import { onMount } from "svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  export let downloadToken;

  const downloadUrl = `/data_download/${downloadToken}`
  let downloadPrepared = false;

  onMount(() => {
    // FIXME use `XMLHttpRequest` instead to avoid `fetch`'s browser-specific timeout?
    fetch(downloadUrl, { redirect: "follow" })
      .then((response) => {
        downloadPrepared = true;
        window.location.assign(response.url);
      })
      .catch((err) => {
        console.error(err);
      });
  });

  function beforeDownload() {
    downloadPrepared = true;
  }
</script>


{#if downloadPrepared}
  <p>
    Your download is ready. You can close this tab once the download starts.
    (If you don't see a prompt to save the file, follow this <a href={downloadUrl} download="{downloadToken}.zip">download link</a>.)
  </p>

{:else}
  <LoadingIndicator
    message="Please wait: your download is being prepared. Large downloads may take a minute or two."
  />

{/if}
