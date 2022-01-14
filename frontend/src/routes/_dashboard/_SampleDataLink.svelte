<script>
  import SampleDataViewerIcon from "$lib/components/icons/SampleDataViewerIcon.svelte";
</script>


<a
  aria-label="View and download sample data"
  title="View and download sample data"
  href="/samples"
>
  <SampleDataViewerIcon
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
  padding: .4rem .2rem .2rem 0;
}
</style>
