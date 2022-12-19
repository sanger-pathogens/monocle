<script>
  import StatusPane from "./StatusPane.svelte";

  export let batches;
</script>

<StatusPane>
  <h3>
    <code>{batches.received}</code> Sample{batches.received === 1 ? "" : "s"} Received
  </h3>

  <table>
    <tr>
      <th>batch</th>
      <th>received on</th>
      <th># samples</th>
    </tr>
    {#each batches.deliveries as { name, date, number } (name)}
      <tr>
        <td>{name}</td>
        <td>{date}</td>
        <td>{number}</td>
      </tr>
    {/each}
  </table>
</StatusPane>

<style>
  table {
    max-width: 21rem;
  }
</style>
