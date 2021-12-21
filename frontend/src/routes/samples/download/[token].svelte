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

  const prepareDownloadPromise = new Promise((resolve, reject) => {
    // We don't use `fetch` here to avoid browser-specific timeouts.
    const ajaxRequest = new XMLHttpRequest();
    const onDownloadPrepared = () => {
      window.location.assign(ajaxRequest.responseURL);
      resolve();
    };
    const onError = () => {
      const status = ajaxRequest.status;
      console.error(`GET ${downloadUrl} error: ${ajaxRequest.statusText}`);
      if (status >= 400 && status < 500) {
        reject("Download might have expired. Please close the tab and start new download.");
      }
      else {
        reject("Download error. Please try again by reloading the page.");
      }
    };
    const onCancel = () => {
      console.error("Download was cancelled. Refresh the page to start again.");
    };

    ajaxRequest.addEventListener("load", onDownloadPrepared);

    ajaxRequest.addEventListener("error", onError);
    ajaxRequest.addEventListener("abort", onCancel);

    ajaxRequest.open("GET", downloadUrl);
    ajaxRequest.send();
  });
</script>


{#await prepareDownloadPromise}
  <LoadingIndicator
    message="Please wait: your download is being prepared. Large downloads may take a minute or two."
  />

{:then}
  <p>
    Your download is ready. You can close this tab once the download starts.
    (If you don't see a prompt to save the file, follow this <a href={downloadUrl} download="{downloadToken}.zip">download link</a>.)
  </p>

{:catch error}
  <p>{error}</p>

{/await}
