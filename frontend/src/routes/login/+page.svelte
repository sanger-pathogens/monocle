<script>
  import { HTTP_POST, HTTP_HEADERS_JSON } from "$lib/constants.js";
  import { sessionStorageAvailable } from "$lib/utils/featureDetection.js";

  let username;
  let password;
  let submitting;

  $: formComplete = username?.trim() && password?.trim();

  function onSubmit() {
    if (!formComplete) {
      return;
    }

    submitting = true;
    logIn(username, password, fetch)
      .then((response) => {
        if (response.redirected) {
          clearSessionStorage();
          // Below we redirect by `window.location` reassignment instead of using SvelteKit's `goto()`
          // because we need to force `__layout` component to re-render to re-fetch project and user deatils after the login.
          window.location.href = response.url;
        }
      })
      .catch((err) => {
        console.error(`Error while logging in: ${err}`);
        alert(
          "An error occured while submitting the credentials. Please try again and contact us if the problem persists."
        );
      })
      .finally(() => (submitting = false));
  }

  function logIn(usernameParam, passwordParam, fetch) {
    return fetch("/auth", {
      method: HTTP_POST,
      headers: HTTP_HEADERS_JSON,
      body: JSON.stringify({
        username: usernameParam,
        password: passwordParam,
      }),
    });
  }

  function clearSessionStorage() {
    if (sessionStorageAvailable()) {
      sessionStorage.clear();
    }
  }
</script>

<h2 id="login-heading">Log in</h2>

<form aria-labelledby="login-heading" on:submit|preventDefault={onSubmit}>
  <fieldset disabled>
    <legend>Project (coming soon)</legend>
    <label class="label-radio">
      JUNO
      <input type="radio" name="project" value="juno" checked />
    </label>
    <label class="label-radio">
      GPS
      <input type="radio" name="project" value="gps" />
    </label>
  </fieldset>

  <label>
    Username
    <input bind:value={username} minlength="3" maxlength="256" />
  </label>

  <label>
    Password
    <input
      type="password"
      bind:value={password}
      minlength="3"
      maxlength="256"
    />
  </label>

  <button
    type="submit"
    class="primary btn-wide"
    on:click|preventDefault={onSubmit}
    disabled={!formComplete || submitting}
  >
    Log in
  </button>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  fieldset {
    margin-bottom: 0;
    text-align: center;
  }
  legend {
    margin: 0 auto 0.4rem;
  }

  input:not([type="radio"]) {
    width: 14rem;
    max-width: 78vw;
  }

  button {
    margin-top: 1rem;
  }
</style>
