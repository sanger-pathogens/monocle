<script>
  import Card from "$lib/components/Card.svelte";

  export let batches;
</script>


<Card>
  <h4>
    <code>{batches.received}</code> Sample{batches.received === 1 ? "" : "s"} Received
  </h4>

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
</Card>


<style>
</style>
