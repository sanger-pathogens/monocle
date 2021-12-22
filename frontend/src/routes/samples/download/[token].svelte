<script context="module">
  // Extract `token` from the URL path and pass it to the page component as a prop.
  export function load({ page }) {
    return { props: { downloadToken: page.params.token } };
  }
</script>

<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  export let downloadToken;

  const HTTP_TIMEOUT_STATUS_CODE = 504;
  const downloadUrl = `/data_download/${downloadToken}`

  const prepareDownloadPromise = new Promise((resolve, reject) => {
    // We don't use `fetch` here to avoid browser-specific timeouts.
    const ajaxRequest = new XMLHttpRequest();

    const onLoad = (event) => {
      // At least the 504 Gateway Timeout error ends up in the "load" event and not in "error" event (ie it's treated as
      // success. Don't ask me why.
      if (ajaxRequest.status >= 400) {
        onError(event);
      }
      else {
        window.location.assign(ajaxRequest.responseURL);
        resolve();
      }
    };

    const onError = () => {
      const status = ajaxRequest.status;
      console.error(`GET ${downloadUrl} error: ${ajaxRequest.statusText || "uknown"}`);
      if (status >= 400 && status < 500) {
        reject("Download might have expired. Please close the tab and start new download.");
      }
      else if (status === HTTP_TIMEOUT_STATUS_CODE) {
        reject("Timeout error. Please reduce the download size and try again.");
      }
      else {
        reject("Download error. Please try again by reloading the page or try to reduce the download size.");
      }
    };

    const onCancel = () => {
      reject("Download was cancelled. Refresh the page to start again or try to reduce the download size.");
    };

    ajaxRequest.addEventListener("load", onLoad);
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
