<script>
  import { getStores } from "$app/stores";
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";
  import AppMenu from "../_app-menu/_index.svelte";

  export let session = getStores().session;
</script>

<AppMenu metadataUploadLink={false} {session} />

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
