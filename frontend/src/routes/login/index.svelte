<script>
  let username;
  let password;
</script>


<h2>Log in</h2>

<form>
  <fieldset>
    <legend>Project</legend>
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
    <input bind:value={username} required />
  </label>

  <label>
    Password
    <input type="password" bind:value={password} required />
  </label>

  <button type="submit" class="primary btn-wide" disabled={!username?.trim() || !password?.trim()}>
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
  margin-bottom: .7rem;
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

