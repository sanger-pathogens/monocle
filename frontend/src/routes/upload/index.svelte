<script>
  import { goto } from '$app/navigation';
  import MetadataUploader from "./_MetadataUploader.svelte";

  function redirectToDashboard() {
    goto("/");
  }
</script>


<h2>Metadata Uploading</h2>
<MetadataUploader on:uploadSuccess={redirectToDashboard} />


<style>
</style>
