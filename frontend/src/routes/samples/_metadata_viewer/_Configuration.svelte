<script>
  import {
    DATA_TYPES,
    EMAIL_MONOCLE_HELP,
    SESSION_STORAGE_KEY_COLUMNS_STATE,
  } from "$lib/constants.js";
  import { deepCopy } from "$lib/utils/copy.js";
  import Dialog from "$lib/components/Dialog.svelte";
  import SettingsIcon from "$lib/components/icons/SettingsIcon.svelte";
  import { sessionStorageAvailable } from "$lib/utils/featureDetection.js";
  import { columnsStore, filterStore } from "../_stores.js";
  import ColumnSelection from "./_ColumnSelection.svelte";

  const KEY_DISABLED = "disabled";
  const KEY_SELECTED = "selected";

  let hasDisabledItems;
  let isOpen;

  $: columnNamesWithActiveFilters = Object.keys($filterStore).reduce(
    (accumColumnNamesWithActiveFilters, dataType) => {
      const columnNames = new Set();
      const filterStateForThisDataType = $filterStore[dataType];
      Object.keys(filterStateForThisDataType).forEach((columnName) => {
        if (filterStateForThisDataType[columnName]?.values?.length) {
          columnNames.add(columnName);
        }
      });
      accumColumnNamesWithActiveFilters[dataType] = columnNames;
      return accumColumnNamesWithActiveFilters;
    },
    {}
  );

  $: columnsPerDatatype = getColumnsStateWithDisabledColumnsWithActiveFilters(
    columnNamesWithActiveFilters
  );

  function apply() {
    // Assign to trigger reactivity. See
    // https://svelte.dev/docs#component-format-script-2-assignments-are-reactive
    $columnsStore = columnsPerDatatype;
    saveColumnsStateToLocalStorage();
  }

  function restoreDefaults() {
    if (
      !hasDisabledItems ||
      confirm("Restoring default columns will remove all filters. Proceed?")
    ) {
      filterStore.removeAllFilters();
      columnsStore.setToDefault();
      saveColumnsStateToLocalStorage();
    }
  }

  function saveColumnsStateToLocalStorage() {
    if (sessionStorageAvailable()) {
      sessionStorage.setItem(
        SESSION_STORAGE_KEY_COLUMNS_STATE,
        JSON.stringify($columnsStore, cleanupColumnsStateReplacer)
      );
    }
  }

  function cleanupColumnsStateReplacer(key, value) {
    // Remove `disabled` and falsy `selected` for a stringified columns state:
    return key === KEY_DISABLED
      ? undefined
      : key === KEY_SELECTED && !value
      ? undefined
      : value;
  }

  function getColumnsStateWithDisabledColumnsWithActiveFilters() {
    hasDisabledItems = false;
    if (!$columnsStore) {
      return;
    }
    return DATA_TYPES.reduce((accumColumnsState, dataType) => {
      const columnNamesOfThisDataTypeWithActiveFilters =
        columnNamesWithActiveFilters[dataType];
      accumColumnsState[dataType]?.forEach((category) =>
        category.columns.forEach((column) => {
          const hasActiveFilter =
            columnNamesOfThisDataTypeWithActiveFilters.has(column.name);
          column.disabled = hasActiveFilter;
          if (hasActiveFilter) {
            hasDisabledItems = true;
          }
        })
      );
      return accumColumnsState;
    }, deepCopy($columnsStore));
  }
</script>

<button on:click={() => (isOpen = true)} class="compact">
  Select columns <SettingsIcon />
</button>

<Dialog ariaLabelledby="column-config-heading" bind:isOpen isWide={true}>
  <h4 id="column-config-heading">Select displayed columns</h4>

  {#if Object.keys(columnsPerDatatype || {}).length}
    <form>
      <fieldset class="all-data-types-container">
        <ColumnSelection columnsData={columnsPerDatatype.metadata}>
          Metadata
        </ColumnSelection>

        <ColumnSelection columnsData={columnsPerDatatype["in silico"]}>
          <i>In silico</i> analysis
        </ColumnSelection>

        <ColumnSelection
          columnsData={columnsPerDatatype["qc data"]}
          open={false}
        >
          QC
        </ColumnSelection>

        {#if hasDisabledItems}
          <p class="disabled-info">
            * To de-select a column with an active filter, first remove the
            filter.
          </p>
        {/if}
      </fieldset>

      <fieldset class="end-btns">
        <button
          class="primary"
          on:click|preventDefault={() => {
            apply();
            isOpen = false;
          }}
          type="submit"
        >
          Apply and close
        </button>
        <button on:click={restoreDefaults} type="button">
          Restore default columns
        </button>
        <button on:click={() => (isOpen = false)} type="button"> Close </button>
      </fieldset>
    </form>
  {:else}
    <p>
      Something went wrong. Please try to reload the page and <a
        href={`mailto:${EMAIL_MONOCLE_HELP}`}>contact us</a
      > if the problem persists.
    </p>
    <button class="compact close-err-btn" on:click={() => (isOpen = false)}>
      Close
    </button>
  {/if}
</Dialog>

<style>
  form {
    display: flex;
    flex-direction: column;
  }

  fieldset {
    margin-bottom: 0;
  }

  .all-data-types-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    min-height: 10rem;
  }
  @media (min-width: 900px) {
    .all-data-types-container {
      width: 47rem;
    }
  }

  .disabled-info {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin: 0 0 2.3rem;
  }

  .end-btns {
    align-self: center;
  }
  @media (max-width: 680px) {
    .end-btns {
      display: flex;
      flex-direction: column;
    }
  }
  .end-btns button {
    margin-bottom: 0.9rem;
  }

  .close-err-btn {
    display: block;
    margin-left: auto;
    margin-right: auto;
  }
</style>
