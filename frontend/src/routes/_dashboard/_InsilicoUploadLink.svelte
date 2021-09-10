<script>
  import InsilicoUploadIcon from "$lib/components/icons/InsilicoUploadIcon.svelte";

  export let style = undefined;

  const LINK_TITLE = "Upload in-silico data";
</script>


<a
  aria-label={LINK_TITLE}
  title={LINK_TITLE}
  href="/in-silico-upload"
  {style}
>
  <InsilicoUploadIcon
    color="rgba(0,0,0,.35)"
    colorHover="black"
    height={24}
    width={24}
    style="padding: .4rem .6rem 0 .4rem"
  />
</a>
