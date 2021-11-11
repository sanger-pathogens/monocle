<script>
  import { session } from "$app/stores";
  import UploadIcon from "$lib/components/icons/UploadIcon.svelte";

  const LINK_TITLE = "Upload metadata";
  const ROLE_ADMIN = "admin";

  $: isAdmin = $session?.user?.role === ROLE_ADMIN;
</script>


{#if isAdmin}
  <a
    aria-label={LINK_TITLE}
    title={LINK_TITLE}
    href="/metadata-upload"
  >
    <UploadIcon
      color="rgba(0,0,0,.35)"
      colorHover="black"
      height={26}
      width={26}
      style="padding: .4rem .4rem 0"
    />
  </a>
{/if}
