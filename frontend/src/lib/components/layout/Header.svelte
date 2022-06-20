<script>
  import { browser } from "$app/env";
  import { PATHNAME_LOGIN } from "$lib/constants.js";

  export let session;
</script>

<header>
  <h1><a href="/">Monocle</a></h1>
  <nav>
    {#if typeof $session.project !== "undefined" && typeof $session.project.name !== "undefined"}
      <a href={$session.project.project_url} target="_blank" class="juno-link">
        {#if $session.project.logo_url}
          <img
            alt={$session.project.name}
            src={$session.project.logo_url}
            title={$session.project.name}
          />
        {:else}
          {$session.project.name}
        {/if}
      </a>
      {#each $session.project.header_links as hl}
        <a href={hl.url} target="_blank">{hl.label}</a>
      {/each}
    {/if}
    {#if browser && location && !location.pathname.includes(PATHNAME_LOGIN)}
      <a rel="external" href="/logout" class="login-out-link"> Log out </a>
    {/if}
  </nav>
</header>

<style>
  header {
    background: var(--juno-purple);
    overflow-y: auto;
    padding: 1rem 1.2rem;
    position: relative;
    min-height: 4rem;
    max-width: 100%;
  }

  h1 {
    font-size: 2.6rem;
    font-weight: 600;
    margin-top: 0;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
  }
  h1 a:hover {
    text-decoration: none;
  }

  a {
    color: white;
  }

  nav {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    margin: auto;
    max-width: var(--bp-xl);
    min-width: 65rem;
  }

  .login-out-link {
    position: sticky;
    right: 0;
    background: var(--juno-purple);
    box-shadow: 0 0.3rem 1rem 1.4rem var(--juno-purple);
    margin-left: 1rem;
  }

  nav a {
    padding: 0.6rem;
  }

  .juno-link {
    margin-right: auto;
    max-width: 11vw;
  }
  .juno-link img {
    width: 4rem;
  }

  @media (max-width: 890px) {
    header {
      padding: 0.9rem 0;
    }

    h1 {
      font-size: 1.9rem;
      left: 30%;
      margin-top: 0.4rem;
    }

    nav {
      min-width: 43rem;
    }
    nav a {
      font-size: 0.95rem;
    }
  }

  @media (max-width: 460px) {
    h1 {
      left: 34%;
    }

    nav {
      min-width: 37rem;
    }
    nav a {
      padding-left: 0.4rem;
      padding-right: 0.4rem;
    }
  }
</style>
