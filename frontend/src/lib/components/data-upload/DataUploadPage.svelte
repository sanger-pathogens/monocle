<script context="module">
  const DESCRIPTION_ELEMENT_ID = "uploading-description";
</script>

<script>
  import DataUploader from "./DataUploader.svelte";
  import Dialog from "$lib/components/Dialog.svelte";

  export let dataType;
  export let fileTypes = undefined;
  export let session;

  let uploadSuccessDialogOpen;

  function openDialog() {
    uploadSuccessDialogOpen = true;
  }
</script>

<h2><slot name="upload-title" /></h2>

<p id={DESCRIPTION_ELEMENT_ID}>
  <slot name="upload-description" />
</p>

<DataUploader
  ariaLabelledby={DESCRIPTION_ELEMENT_ID}
  accept={fileTypes}
  {dataType}
  {session}
  on:uploadSuccess={openDialog}
/>

<Dialog bind:isOpen={uploadSuccessDialogOpen} ariaLabelledby="dialog-title">
  <h3 id="dialog-title">Upload success</h3>

  <p><slot name="success-message" /></p>
  <p>You can <a href="/">go to the dashboard</a> or stay on this page.</p>
</Dialog>

<style>
  p {
    text-align: center;
  }
</style>
