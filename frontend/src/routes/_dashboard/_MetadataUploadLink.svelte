<script>
  import { session } from '$app/stores';
  import UploadIcon from "$lib/components/icons/UploadIcon.svelte";

  const LINK_TITLE = "Upload metadata";
  const ROLE_ADMIN = "admin";

  const isAdmin = $session?.user?.role === ROLE_ADMIN;
</script>


{#if isAdmin}
  <a
    aria-label={LINK_TITLE}
    title={LINK_TITLE}
    href="/upload"
  >
    <UploadIcon
      color="rgba(0,0,0,.5)"
      colorHover="black"
      height={22}
      width={22}
      style="padding: .4rem .4rem 0"
    />
  </a>
{/if}


<style>
a {
  float: right;
  position: sticky;
  top: 1rem;
  right: .6rem;
  z-index: 9;
}
</style>

