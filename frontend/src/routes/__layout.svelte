<script>
  import Header from '$lib/components/layout/Header.svelte';
  import Footer from '$lib/components/layout/Footer.svelte';
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

  --bp-xl: 1400px;

  --width-main: 50rem;
}

main {
  margin: 2rem auto;
  padding-left: 0.8rem;
  padding-right: 0.8rem;
  /* Pages can redefine the variable and thus the width. */
  width: var(--width-main);
  max-width: 100%;
}

:global([role=dialog] .content > h1),
:global([role=dialog] .content > h2),
:global([role=dialog] .content > h3),
:global([role=dialog] .content > h4),
:global([role=dialog] .content > h5),
:global([role=dialog] .content > h6) {
  font-size: 1.1rem;
}

:global(button.light) {
  background: var(--background-body);
  border: 1px solid var(--background);
  font-weight: 100;
}
</style>
