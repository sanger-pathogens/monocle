<script context="module">
  const LINK_TITLE_METADATA_UPLOAD = "Upload metadata";
  const LINK_TITLE_IN_SILICO_UPLOAD = "Upload in-silico data";
  const LINK_TITLE_QC_DATA_UPLOAD = "Upload QC data";
</script>

<script>
  import { USER_ROLE_ADMIN } from "$lib/constants.js";
  import UploadMenuIcon from "$lib/components/icons/UploadMenuIcon.svelte";

  export let session;

  $: isAdmin = $session?.user?.role === USER_ROLE_ADMIN;
</script>

{#if isAdmin}
  <UploadMenuIcon
    color="rgba(0,0,0,.35)"
    focusable={true}
    style="padding: 0.4rem 0.4rem 0.5rem 0.7rem"
    cssClass="dropdown-menu-trigger"
  />

  <nav class="dropdown-menu-items">
    <a
      aria-label={LINK_TITLE_METADATA_UPLOAD}
      title={LINK_TITLE_METADATA_UPLOAD}
      href="/metadata-upload"
    >
      Metadata
    </a>
    <a
      aria-label={LINK_TITLE_IN_SILICO_UPLOAD}
      title={LINK_TITLE_IN_SILICO_UPLOAD}
      href="/in-silico-upload"
    >
      <i>In silico</i> data
    </a>
    <a
      aria-label={LINK_TITLE_QC_DATA_UPLOAD}
      title={LINK_TITLE_QC_DATA_UPLOAD}
      href="/qc-data-upload"
    >
      QC data
    </a>
  </nav>
{/if}

<style>
  .dropdown-menu-items {
    position: absolute;
    right: 0;
    top: 4rem;
    background: var(--background-body);
    border: 1px solid var(--color-border);
    border-radius: 2px;
    box-shadow: 0 0.2rem 0.4rem rgba(48, 55, 66, 0.2);
    padding: 0.4rem 0;
    white-space: nowrap;
  }

  .dropdown-menu-items a {
    display: block;
    color: var(--text-muted);
    padding: 0.2rem 0.7rem;
  }
</style>
