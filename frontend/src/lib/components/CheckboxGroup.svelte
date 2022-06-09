<script context="module">
  const DEFAULT_KEY_CHECKED = "checked";
  const DEFAULT_ITEMS_NAME = "items";
  const RE_SPACE = /\s/;
  const UNDERSCORE = "_";
</script>

<script>
  import { onMount } from "svelte";

  export let checkedKey = DEFAULT_KEY_CHECKED;
  export let disabledTooltip = undefined;
  export let disabledSuffix = undefined;
  export let groupName;
  export let items = [];
  export let itemsName = DEFAULT_ITEMS_NAME;

  const ID_GROUP_CHECKBOX = `cb-group-${groupName.replace(
    RE_SPACE,
    UNDERSCORE
  )}`;

  let expanded = areOnlySomeChecked();
  let groupCheckbox;
  let numSelectedItems = items.reduce(
    (accumCount, item) => (item[checkedKey] ? accumCount + 1 : accumCount),
    0
  );

  $: {
    if (groupCheckbox) {
      groupCheckbox.indeterminate = areOnlySomeChecked(items);
    }
  }

  onMount(() => {
    // `indeterminate` can only be set via JS, not HTML, so we have to use `onMount` to
    // make sure the group checkbox is in the DOM to use it here.
    if (groupCheckbox) {
      groupCheckbox.indeterminate = areOnlySomeChecked(items);
    }
  });

  function onGroupCheckboxChange() {
    if (areAllChecked()) {
      uncheckItems();
    } else if (areAllUnchecked()) {
      checkItems();
    } else {
      groupCheckbox.checked = false;
      uncheckItems();
    }
  }

  function areAllChecked() {
    return items.every((item) => item[checkedKey]);
  }

  function areAllUnchecked() {
    return items.every((item) => !item[checkedKey]);
  }

  function areOnlySomeChecked() {
    return !(areAllChecked() || areAllUnchecked());
  }

  function checkItems() {
    items.forEach((item) => (item[checkedKey] = true));
    // Re-assign to trigger reactivity. See
    // https://svelte.dev/docs#component-format-script-2-assignments-are-reactive
    items = items;
    numSelectedItems = items.length;
  }

  function uncheckItems() {
    items.forEach((item) => (item[checkedKey] = false));
    // Re-assign to trigger reactivity. See
    // https://svelte.dev/docs#component-format-script-2-assignments-are-reactive
    items = items;
    numSelectedItems = 0;
  }
</script>

{#if items.length}
  <dl>
    <dt>
      <input
        type="checkbox"
        id={ID_GROUP_CHECKBOX}
        checked={areAllChecked(items)}
        on:change={onGroupCheckboxChange}
        bind:this={groupCheckbox}
      />
      <label
        aria-label={`${
          expanded ? "Hide" : "Show"
        } available ${itemsName} for category "${groupName}"`}
        for={ID_GROUP_CHECKBOX}
        on:click|preventDefault={() => (expanded = !expanded)}
      >
        <span class="expand-icon">{expanded ? "▼" : "▶"}</span>
        {groupName} [<code>{numSelectedItems}/{items.length}</code>]
      </label>
    </dt>

    {#if expanded}
      {#each items as item (item.displayName)}
        {@const displayDisabledTooltip = item.disabled && disabledTooltip}
        <dd title={displayDisabledTooltip ? disabledTooltip : null}>
          <label class:disabled={item.disabled}>
            <input
              type="checkbox"
              bind:checked={item[checkedKey]}
              on:change={(event) =>
                event.currentTarget.checked
                  ? ++numSelectedItems
                  : --numSelectedItems}
              disabled={item.disabled}
            />
            {item.displayName}{item.disabled && disabledSuffix
              ? disabledSuffix
              : ""}
            {#if displayDisabledTooltip}
              <span class="sr-only">{disabledTooltip}</span>
            {/if}
          </label>
        </dd>
      {/each}
    {/if}
  </dl>
{/if}

<style>
  dt {
    margin-bottom: 0.5rem;
    white-space: pre;
  }

  .expand-icon {
    color: var(--text-main);
    font-size: 0.7rem;
  }
</style>
