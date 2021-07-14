<script>
  export let errors = [];
</script>


{#if errors.length}
  <p role="alert" aria-live="polite">
    <span aria-hidden="true">⚠️ </span>The {errors.length ? "following files" : "file"} couldn't be uploaded because of the validation errors:
  </p>
{/if}
{#each errors as {fileName, errorMessages}, i}
  <details open={i === 0}>
    <summary>
      <code>{fileName}</code>
    </summary>
    <ul>
      {#each errorMessages as error, j (error)}
        <li>
          <input type="checkbox" aria-hidden="true" id="validation-error-{i}-{j}" >
          <label for="validation-error-{i}-{j}">{error}</label>
        </li>
      {/each}
    </ul>
  </details>
{/each}


<style>
ul {
  list-style: none;
  padding-left: 0;
}

input:checked + label {
  text-decoration: line-through;
}

label {
  cursor: pointer;
}
</style>
