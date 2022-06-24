<script>
  import { USER_ROLE_ADMIN } from "$lib/constants.js";
  import UploadIcon from "$lib/components/icons/UploadIcon.svelte";

  export let session;

  const LINK_TITLE = "Upload metadata";

  $: isAdmin = $session?.user?.role === USER_ROLE_ADMIN;
</script>

{#if isAdmin}
  <a aria-label={LINK_TITLE} title={LINK_TITLE} href="/metadata-upload">
    <UploadIcon
      color="rgba(0,0,0,.35)"
      colorHover="black"
      height={26}
      width={26}
      style="padding: .4rem .4rem 0"
    />
  </a>
{/if}
