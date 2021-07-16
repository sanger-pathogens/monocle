<script>
  import Dialog from "$lib/components/Dialog.svelte";

  export let failures = [];
  export let title;

  let dialogOpen;
</script>


{#if failures.length}
  <button on:click={() => dialogOpen = true} class="light">
    Show fail messages
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
  </Dialog>
{/if}


<style>
button {
  display: block;
  margin: .9rem 0 0;
}

.fail-msg-column {
  width: 48%;
}
</style>

