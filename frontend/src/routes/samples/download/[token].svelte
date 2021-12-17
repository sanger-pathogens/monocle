<script>
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";

  const downloadToken = window.location.pathname.split("/").pop();
  const downloadUrl = `/data_download/${downloadToken}`
</script>


<svelte:head>
  <meta http-equiv="refresh" content="0; url={downloadUrl}" />
</svelte:head>

<LoadingIndicator
  message="Please wait: your download is being prepared. Large downloads may take a minute or two."
/>
