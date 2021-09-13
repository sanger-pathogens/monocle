<script>
  import Dialog from "$lib/components/Dialog.svelte";

  export let failures = [];
  export let title;

  let dialogOpen;
  let hasFailureMessages = failures.length;
  let hasNestedComponents = $$slots?.default;
</script>


{#if hasFailureMessages || hasNestedComponents}
  <button on:click={() => dialogOpen = true}>
    Show failed
  </button>

  <Dialog bind:isOpen={dialogOpen}>
    <h4>{title}</h4>

    <table>
      <tr>
        <th>lane</th>
        <th>stage</th>
        <th class="fail-msg-column">fail message</th>
      </tr>
      {#each failures as { lane, stage, issue } (lane+stage+issue)}
        <tr>
          <td>{lane}</td>
          <td>{stage}</td>
          <td>{issue}</td>
        </tr>
      {/each}
    </table>

    <slot></slot>
  </Dialog>
{/if}


<style>
table {
  margin-bottom: 1rem;
}

.fail-msg-column {
  width: 48%;
}
</style>

