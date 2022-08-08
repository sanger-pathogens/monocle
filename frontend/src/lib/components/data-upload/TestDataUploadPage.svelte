<!-- This component is simply a wrapper around <DataUploadPage /> for testing purposes: it's
a temporary workaround for testing a component w/o default slots (see
https://github.com/testing-library/svelte-testing-library/issues/48#issuecomment-522029988).-->
<script>
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";
</script>

<DataUploadPage {...$$restProps}>
  <svelte:fragment slot="upload-title">Data upload</svelte:fragment>

  <svelte:fragment slot="upload-description">
    Select or drag and drop your files:
  </svelte:fragment>

  <svelte:fragment slot="success-message">
    All files were successfully uploaded.
  </svelte:fragment>
</DataUploadPage>
