<script>
  import { getStores } from "$app/stores";
  import DataUploadPage from "$lib/components/data-upload/DataUploadPage.svelte";
  import AppMenu from "../_app-menu/_index.svelte";

  export let session = getStores().session;
</script>

<AppMenu inSilicoDataUploadLink={false} {session} />

<DataUploadPage
  dataType="in silico"
  fileTypes="text/plain,.txt,text/tab-separated-values,.tsv,.tab"
  {session}
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
