<script context="module">
  const TOP_OFFSET_REDUCED = "2rem";
</script>

<script>
  import DataUploadLinks from "./DataUploadLinks.svelte";
  import SampleDataLink from "./SampleDataLink.svelte";

  export let sampleDataLink = true;
  export let metadataUploadLink = true;
  export let qcDataUploadLink = true;
  export let inSilicoDataUploadLink = true;
</script>

<nav>
  {#if sampleDataLink}
    <SampleDataLink />
  {/if}
  <DataUploadLinks
    {metadataUploadLink}
    {qcDataUploadLink}
    {inSilicoDataUploadLink}
    topOffset={sampleDataLink ? undefined : TOP_OFFSET_REDUCED}
  />
</nav>

<style>
  nav {
    display: flex;
    flex-direction: column;
    align-self: flex-end;
    margin-right: -1rem;

    position: sticky;
    top: 1rem;
    z-index: 9;
  }
  @media (min-width: 2000px) {
    /* This pushes the menu w/ the upload buttoms further to the right for larger screens. */
    nav {
      margin-right: -8rem;
    }
  }
</style>
