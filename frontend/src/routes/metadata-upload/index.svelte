<script>
  import DataUploader from "$lib/components/data-upload/DataUploader.svelte";
  import Dialog from "$lib/components/Dialog.svelte";

  const DESCRIPTION_ELEMENT_ID = "metadata-uploading-description";

  let uploadSuccessDialogOpen;

  function openDialog() {
    uploadSuccessDialogOpen = true;
  }
</script>


<h2>Metadata upload</h2>

<p id={DESCRIPTION_ELEMENT_ID}>Select or drag and drop your CSV files (saved as UTF-8) with sample metadata:</p>

<DataUploader
  ariaLabelledby={DESCRIPTION_ELEMENT_ID}
  uploadUrl="/metadata/juno/metadata-upload"
  on:uploadSuccess={openDialog}
/>

<Dialog bind:isOpen={uploadSuccessDialogOpen} ariaLabelledby="dialog-title">
  <h3 id="dialog-title">Upload success</h3>

  <p>All metadata were successfully uploaded.</p>
  <p>You can <a href="/">go to the dashboard</a> or stay on this page.</p>
</Dialog>


<style>
p {
  text-align: center;
}
</style>
