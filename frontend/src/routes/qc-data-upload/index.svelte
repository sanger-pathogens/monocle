<script>
  import { getStores } from "$app/stores";
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";

  export let session = getStores().session;
</script>

<DataUploadPage dataType="qc data" {session}>
  <svelte:fragment slot="upload-title">QC data upload</svelte:fragment>

  <svelte:fragment slot="upload-description">
    Select or drag and drop your CSV files (saved as UTF-8) with sample QC data:
  </svelte:fragment>

  <svelte:fragment slot="success-message">
    All QC data were successfully uploaded.
  </svelte:fragment>
</DataUploadPage>
