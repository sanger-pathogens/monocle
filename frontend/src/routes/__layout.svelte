<script>
  import { onMount } from "svelte";
  import { getStores } from "$app/stores";
  import { getUserDetails } from "$lib/dataLoading.js";
  import Header from "$lib/components/layout/Header.svelte";
  import Footer from "$lib/components/layout/Footer.svelte";
  import "../base.css";

  const { session } = getStores();

  onMount(() => {
    getUserDetails(fetch)
      .then(({ type: userRole } = {}) => {
        if (userRole) {
          session.set({ user: { role: userRole } });
        }
      })
      .catch((err) => {
        console.error(err);
      });
  });
</script>


<Header />

<main>
  <slot></slot>
</main>

<Footer />


<style>
:root {
  --juno-indigo: #484885;
  --juno-purple: #6868be;
  --color-border: #dfe3e6;
  --color-link-visited: #663399;
  --color-table-alt-row: #f8f8f8;
  --color-table-hover-row: #f0f0f0;

  --bp-xl: 1400px;

  --width-main: min(98vw, var(--bp-xl));
  --width-reading: 50rem;
}

main {
  box-sizing:border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2rem auto;
  padding-left: 0.8rem;
  padding-right: 0.8rem;
  width: var(--width-main);
  max-width: 100%;
}

:global(.frappe-chart .title) {
  font-size: 1rem;
}

:global([role=dialog] .content > h1),
:global([role=dialog] .content > h2),
:global([role=dialog] .content > h3),
:global([role=dialog] .content > h4),
:global([role=dialog] .content > h5),
:global([role=dialog] .content > h6) {
  font-size: 1.1rem;
}

:global(table.dense td) {
  font-size: .95rem;
  padding: .3rem;
}
@media (min-width: 1278px) {
  :global(table.dense td) {
    padding: .5rem;
  }
}

:global(a[role=button]):hover {
  text-decoration: none;
}

:global(button),
:global([role=button]),
:global(input[type="button"]),
:global(input[type="submit"]) {
  border-color: var(--color-border);
}

:global(button.compact),
:global([role=button].compact),
:global(input[type="button"].compact),
:global(input[type="submit"].compact) {
  font-size: 0.95rem;
  padding: 0.5rem;
}

:global(button.primary),
:global([role=button].primary) {
  background: var(--background-body);
  color: var(--juno-indigo);
  border: 1px solid var(--juno-indigo);
  font-weight: 300;
}
</style>
