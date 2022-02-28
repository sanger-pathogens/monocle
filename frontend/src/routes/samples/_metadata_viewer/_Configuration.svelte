<script>
  import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
  import CheckboxGroup from "$lib/components/CheckboxGroup.svelte";
  import Dialog from "$lib/components/Dialog.svelte";
  import SettingsIcon from "$lib/components/icons/SettingsIcon.svelte";
  import { localStorageAvailable } from "$lib/utils/featureDetection.js";
  import { columnsStore } from "../_stores.js";

  let isOpen;

  function apply() {
    // Re-assign to trigger reactivity. See
    // https://svelte.dev/docs#component-format-script-2-assignments-are-reactive
    $columnsStore = $columnsStore;
    if (localStorageAvailable()) {
      localStorage.setItem("columnsState", JSON.stringify($columnsStore));
    }
  }
</script>


<button
  on:click={() => isOpen = true}
  class="compact"
>
  Select columns <SettingsIcon />
</button>

<Dialog
  ariaLabelledby="column-config-heading"
  bind:isOpen
  isWide={true}
>
  <h4 id="column-config-heading">Select displayed columns</h4>

  {#if Object.keys($columnsStore || []).length}
    <form>
      <!-- FIXME remove this outer container? -->
      <fieldset class="all-data-types-container">
        {#if $columnsStore.metadata?.length}
          <details open>
            <summary>Metadata</summary>
            {#each $columnsStore.metadata as { name, columns } (name)}
              <CheckboxGroup
                groupName={name}
                items={columns}
                itemsName="columns"
                checkedKey="selected"
              />
            {/each}
          </details>
        {/if}

        {#if $columnsStore["in silico"]?.length}
          <details open>
            <summary><i>In silico</i> analysis</summary>
            {#each $columnsStore["in silico"] as { name, columns } (name)}
              <CheckboxGroup
                groupName={name}
                items={columns}
                itemsName="columns"
                checkedKey="selected"
              />
            {/each}
          </details>
        {/if}
      </fieldset>

      <fieldset class="end-btns">
        <button
          class="primary"
          on:click|preventDefault={() => {apply(); isOpen = false;}}
          type="submit"
        >
          Apply and close
        </button>
        <button
          on:click={columnsStore.setToDefault}
          type="button"
        >
          Restore default columns
        </button>
        <button
          on:click={() => isOpen = false}
          type="button"
        >
          Close
        </button>
      </fieldset>
    </form>

  {:else}
    <p>Something went wrong. Please try to reload the page and <a href={`mailto:${EMAIL_MONOCLE_HELP}`}>contact us</a> if the problem persists.</p>
    <button class="compact" on:click={() => isOpen = false}>
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

details {
  padding-right: 1rem;
  width: 20rem;
}
summary {
  padding-left: 2rem;
  text-align: left;
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
  margin-bottom: .9rem;
}
</style>
