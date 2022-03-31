<script>
  import { HTTP_POST, HTTP_HEADERS_JSON } from "$lib/constants.js"

  let username;
  let password;

  $: formComplete = username?.trim() && password?.trim();

  function onSubmit() {
    if (!formComplete) {
      return;
    }

    logIn(username, password, fetch)
      .catch((err) => {
        console.error(`Error while logging in: ${err}`);
        alert(
          "An error occured while submitting the credentials. Please try again and contact us if the problem persists.");
      });
  }

  function logIn(usernameParam, passwordParam, fetch) {
    return fetch("/auth", {
      method: HTTP_POST,
      headers: HTTP_HEADERS_JSON,
      body: JSON.stringify({ username: usernameParam, password: passwordParam })
    });
  }
</script>


<h2>Log in</h2>

<form on:submit|preventDefault={onSubmit}>
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
    <input type="password" bind:value={password} minlength="3" maxlength="256" />
  </label>

  <button
    type="submit"
    class="primary btn-wide"
    on:click|preventDefault={onSubmit}
    disabled={!formComplete}
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
  margin: 0 auto .4rem;
}

input {
  width: 14rem;
  max-width: 78vw;
}

button {
  margin-top: 1rem;
}
</style>

