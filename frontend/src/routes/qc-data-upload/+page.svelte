<script>
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";
  import { projectStore } from "../stores.js";
  import AppMenu from "../_app-menu/index.svelte";
</script>

<AppMenu qcDataUploadLink={false} />

<DataUploadPage
  dataType="qc data"
  fileTypes="text/plain,.txt,text/tab-separated-values,.tsv,.tab"
  uploadLinks={$projectStore?.uploadLinks}
>
  <svelte:fragment slot="upload-title">QC data upload</svelte:fragment>

  <svelte:fragment slot="upload-description">
    Select or drag and drop your files with tab-separated QC data:
  </svelte:fragment>

  <svelte:fragment slot="success-message">
    All QC data were successfully uploaded.
  </svelte:fragment>
</DataUploadPage>
