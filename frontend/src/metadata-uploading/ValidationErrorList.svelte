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
      {#each errorMessages as error, j}
        <li>
          <input type="checkbox" aria-hidden="true" id="validation-error-{i}-{j}" >
          <label for="validation-error-{i}-{j}">{error}</label>
        </li>
      {/each}
    </ul>
  </details>
{/each}


<style>
input:checked + label {
  text-decoration: line-through;
}
/* FIXME: the CSS below is temporary: it'll be removed or updated once
the dashboard CSS is updated in https://trello.com/c/X66mRnj3/130-recreate-dashboard-in-javascript */
p {
  margin-bottom: revert;
  text-align: center;
}
summary {
  cursor: pointer;
  font-size: 1.35rem;
  padding-bottom: 1rem;
}
ul {
  list-style: none;
}
li {
  display: flex;
  align-items: flex-start;
}
label {
  cursor: pointer;
  display: inline;
}
input {
  margin-right: 0.5rem;
  margin-top: 0.6rem;
}
</style>
