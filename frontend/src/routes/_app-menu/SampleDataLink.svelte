<script>
  import BulkDownloadIcon from "$lib/components/icons/BulkDownloadIcon.svelte";
</script>

<a
  aria-label="Download sample data"
  title="Download sample data"
  href="/samples"
>
  <BulkDownloadIcon
    color="rgba(0,0,0,.35)"
    colorHover="black"
    height={23}
    width={23}
  />
</a>

<style>
  a {
    display: flex;
    justify-content: center;
    padding: 0.4rem 0.2rem 0.2rem 0;
  }
</style>
