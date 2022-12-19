<script>
  import { onMount } from "svelte";
  import { getUserDetails, getProjectInformation } from "$lib/dataLoading.js";
  import Header from "$lib/components/layout/Header.svelte";
  import Footer from "$lib/components/layout/Footer.svelte";
  import { projectStore, userStore } from "./stores.js";
  import "../base.css";
  import "../simplecookie.css";

  export const ssr = false;

  onMount(() => {
    appendScriptToHead("/files/simplecookie.min.js", { async: true });

    getUserDetails(fetch)
      .then(({ type: userRole } = {}) => {
        if (userRole) {
          userStore.setRole(userRole);
        }
      })
      .catch((err) => {
        console.error(err);
      });

    getProjectInformation(fetch).then((project) =>
      projectStore.setFromResponse(project)
    );
  });

  function appendScriptToHead(src, options) {
    const script = document.createElement("script");
    script.src = src;
    Object.keys(options).forEach(
      (optionKey) => (script[optionKey] = options[optionKey])
    );
    document.head.appendChild(script);
  }
</script>

<Header projectState={$projectStore} />

<main>
  <slot />
</main>

<Footer contacts={$projectStore?.contacts} />

<style>
  :root {
    --juno-indigo: #484885;
    --juno-purple: #6868be;
    --color-danger: #e66969;
    --color-link-visited: #663399;
    --color-table-alt-row: #f8f8f8;
    --color-table-hover-row: #f0f0f0;

    --bp-xl: 1400px;

    --width-main: min(98vw, var(--bp-xl));
    --width-reading: 50rem;

    /* This CSS variable sets the background color of an item for `svelte-select`.
  See https://github.com/rob-balfre/svelte-select/blob/master/docs/theming_variables.md */
    --multiItemBG: var(--background);
  }

  main {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 2rem auto;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
    width: var(--width-main);
    max-width: 100%;
  }

  :global(.dropdown-menu-trigger:not(:hover):not(:focus)
      + .dropdown-menu-items:not(:hover):not(:focus-within)) {
    /* Hide visually only while still show the menu to assistive technology like screen readers: */
    clip: rect(0 0 0 0);
    clip-path: inset(50%);
    height: 1px;
    overflow: hidden;
    white-space: nowrap;
    width: 1px;
    /* END hide visually only */
  }

  :global(.frappe-chart .title) {
    font-size: 1rem;
  }

  :global([role="dialog"] .content > h1),
  :global([role="dialog"] .content > h2),
  :global([role="dialog"] .content > h3),
  :global([role="dialog"] .content > h4),
  :global([role="dialog"] .content > h5),
  :global([role="dialog"] .content > h6) {
    font-size: 1.1rem;
  }

  :global(.label-radio) {
    display: inline-flex;
    flex-direction: column;
    margin-right: 1rem;
  }

  :global(table.dense th) {
    font-size: 0.95rem;
    padding: 0.5rem;
  }
  :global(table.dense td) {
    font-size: 0.95rem;
    line-height: 1.2;
    padding: 0.3rem;
  }
  @media (min-width: 1278px) {
    :global(table.dense td) {
      padding: 0.5rem;
    }
  }

  :global(a[role="button"]):hover {
    text-decoration: none;
  }

  :global(button.compact),
  :global([role="button"].compact),
  :global(input[type="button"].compact),
  :global(input[type="submit"].compact) {
    font-size: 0.95rem;
    padding: 0.5rem;
  }

  :global(.btn-wide) {
    margin-left: auto;
    margin-right: auto;
    width: 100%;
  }

  :global(button.primary),
  :global([role="button"].primary) {
    background: var(--background-body);
    color: var(--juno-indigo);
    border: 1px solid var(--juno-indigo);
    font-weight: 300;
  }

  :global(button.danger),
  :global([role="button"].danger) {
    color: var(--color-danger);
    border: 1px solid var(--color-danger);
    font-weight: 300;
  }

  :global(.icon-btn) {
    border: none;
    margin-top: 0.25rem;
    padding: 0.3rem 0.3rem 0.1rem;
  }

  :global(.sr-only) {
    /* Credits: https://stackoverflow.com/a/26032207/4579279 */
    position: absolute !important; /* Outside the DOM flow */
    height: 1px;
    width: 1px;
    overflow: hidden;
    clip: rect(1px, 1px, 1px, 1px);
  }
</style>
