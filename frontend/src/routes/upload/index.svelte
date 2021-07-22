<script>
  import Dialog from "$lib/components/Dialog.svelte";
  import MetadataUploader from "./_MetadataUploader.svelte";

  let uploadSuccessDialogOpen;

  function openDialog() {
    uploadSuccessDialogOpen = true;
  }
</script>


<h2>Metadata Uploading</h2>

<MetadataUploader on:uploadSuccess={openDialog} />

<Dialog bind:isOpen={uploadSuccessDialogOpen}>
  <h3>Upload success</h3>

  <p>All metadata were successfully uploaded.</p>
  <p>You can <a href="/">go to dashboard</a> or stay on this page.</p>
</Dialog>
