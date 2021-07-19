<script>
  export let style = undefined;
</script>


<article {style}>
  <slot></slot>
</article>


<style>
article {
  box-sizing:border-box;
  display: inline-block;
  border: 1px solid var(--color-border);
  border-radius: .3rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .1);
  margin: 0 .5rem .9rem;
  padding: 1rem;
  min-width: min(21rem, 100%);
  max-width: 27rem;
}
</style>
