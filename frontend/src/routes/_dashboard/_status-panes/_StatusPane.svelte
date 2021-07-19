<script>
  import Card from "$lib/components/Card.svelte";
</script>


<!-- Above this width the panes start to stack when the fail message modal is open.
So only increase the width if you know what you're doing. -->
<Card style="max-width: 25rem">
  <slot></slot>
</Card>
