<script>
  import DataUploader from "$lib/components/data-upload/DataUploader.svelte";
  import Dialog from "$lib/components/Dialog.svelte";

  const DESCRIPTION_ELEMENT_ID = "in-silico-uploading-description";

  let uploadSuccessDialogOpen;

  function openDialog() {
    uploadSuccessDialogOpen = true;
  }
</script>


<h2>In silico data upload</h2>

<p id={DESCRIPTION_ELEMENT_ID}>Select or drag and drop your files with <em>in silico</em> data:</p>

<DataUploader
  ariaLabelledby={DESCRIPTION_ELEMENT_ID}
  uploadUrl="/metadata/in-silico-upload"
  on:uploadSuccess={openDialog}
/>

<Dialog bind:isOpen={uploadSuccessDialogOpen}>
  <h3>Upload success</h3>

  <p>All <em>in silico</em> data were successfully uploaded.</p>
  <p>You can <a href="/">go to the dashboard</a> or stay on this page.</p>
</Dialog>


<style>
p {
  text-align: center;
}
</style>

