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
:global(:root) {
  --juno-indigo: #484885;
  --juno-purple: #6868be;

  --bp-xl: 1400px;
}

main {
  margin: 1rem auto;
  padding-left: 0.8rem;
  padding-right: 0.8rem;
  width: 50rem;
  max-width: 100%;
}
</style>
