<script>
  import { getStores } from "$app/stores";
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";

  export let session = getStores().session;
</script>

<DataUploadPage dataType="metadata" {session}>
  <svelte:fragment slot="upload-title">Metadata upload</svelte:fragment>

  <svelte:fragment slot="upload-description">
    Select or drag and drop your CSV files (saved as UTF-8) with sample
    metadata:
  </svelte:fragment>

  <svelte:fragment slot="success-message">
    All metadata were successfully uploaded.
  </svelte:fragment>
</DataUploadPage>
