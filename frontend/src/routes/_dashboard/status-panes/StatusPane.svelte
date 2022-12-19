<script>
  import Card from "$lib/components/Card.svelte";

  export let grow = false;
</script>

<!-- Above this width the panes start to stack when the fail message modal is open.
So only increase the width if you know what you're doing. -->
<Card style="max-width: 25rem; flex-grow: {grow ? 1 : 0}">
  <slot />
</Card>
