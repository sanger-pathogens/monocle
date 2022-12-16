<script>
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";
  import { projectStore } from "../_stores.js";
  import AppMenu from "../_app-menu/_index.svelte";
</script>

<AppMenu inSilicoDataUploadLink={false} />

<DataUploadPage
  dataType="in silico"
  fileTypes="text/plain,.txt,text/tab-separated-values,.tsv,.tab"
  uploadLinks={$projectStore?.uploadLinks}
>
  <svelte:fragment slot="upload-title">
    <i>In silico</i> data upload
  </svelte:fragment>

  <svelte:fragment slot="upload-description">
    Select or drag and drop your files with tab-separated <em>in silico</em> data:
  </svelte:fragment>

  <svelte:fragment slot="success-message">
    All <i>in silico</i> data were successfully uploaded.
  </svelte:fragment>
</DataUploadPage>
