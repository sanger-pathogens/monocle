<script>
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";
  import { projectStore } from "../stores.js";
  import AppMenu from "../_app-menu/index.svelte";
</script>

<AppMenu metadataUploadLink={false} />

<DataUploadPage dataType="metadata" uploadLinks={$projectStore?.uploadLinks}>
  <svelte:fragment slot="upload-title">Metadata upload</svelte:fragment>

  <svelte:fragment slot="upload-description">
    Select or drag and drop your CSV files (saved as UTF-8) with sample
    metadata:
  </svelte:fragment>

  <svelte:fragment slot="success-message">
    All metadata were successfully uploaded.
  </svelte:fragment>
</DataUploadPage>
