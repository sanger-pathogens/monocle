<script>
  import CheckboxGroup from "$lib/components/CheckboxGroup.svelte";

  export let columnsData = undefined;
  export let open = true;
</script>

{#if columnsData?.length}
  <details open={open || null}>
    <summary><slot></slot></summary>
    {#each columnsData as { name, columns } (name)}
      <CheckboxGroup
        groupName={name}
        items={columns}
        itemsName="columns"
        checkedKey="selected"
        disabledTooltip="* To de-select this column, first remove the column's filter."
        disabledSuffix="*"
      />
    {/each}
  </details>
{/if}

<style>
  details {
    padding-right: 1rem;
    width: 20rem;
  }
  summary {
    padding-left: 2rem;
    text-align: left;
  }
</style>
