<script>
  import { browser } from "$app/env";
  import { PATHNAME_LOGIN } from "$lib/constants.js";

  export let session;
</script>

<header>
  <h1>
    <a href="/">
      <!-- svelte-ignore a11y-unknown-role -->
      <img
        role="monocle-logo"
        class="monocle-logo"
        src="/imgs/monocleSM_logo.svg"
        alt="Monocle Status Monitor"
        title="Monocle Status Monitor"
      />
    </a>
  </h1>
  <nav>
    {#if $session?.project?.name}
      <a
        href={$session.project.project_url}
        target="_blank"
        class="project-link"
      >
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
      {#each $session.project.header_links as { label, url } (`${label}${url}`)}
        <a href={url} target="_blank">{label}</a>
      {/each}
    {/if}
    {#if browser && location && !location.pathname.includes(PATHNAME_LOGIN)}
      <a rel="external" href="/logout" class="logout-link"> Log out </a>
    {/if}
  </nav>
</header>

<style>
  header {
    background: var(--juno-purple);
    overflow-y: auto;
    padding: 0.5rem 1rem;
    position: relative;
    max-width: 100%;
  }

  h1 {
    margin-top: 1.2rem;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
  }
  h1 a:hover {
    text-decoration: none;
  }

  .monocle-logo {
    max-width: 11rem;
  }

  a {
    color: white;
  }

  nav {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    margin: auto;
    min-height: 5.3rem;
    max-width: var(--bp-xl);
    min-width: 65rem;
  }

  .logout-link {
    position: sticky;
    right: 0;
    background: var(--juno-purple);
    box-shadow: 0 0.3rem 1rem 1.4rem var(--juno-purple);
    margin-left: 1rem;
  }
  .logout-link:only-child {
    /* Keep the logout link rigthmost before project links and logo are loaded: */
    margin-left: auto;
  }

  nav a {
    padding: 0.5rem;
  }

  .project-link {
    margin-right: auto;
    max-width: 11vw;
  }
  .project-link img {
    width: 4rem;
  }

  @media (max-width: 1000px) {
    header {
      padding: 0.9rem 0;
    }

    h1 {
      left: 30%;
      margin-top: 0.4rem;
    }

    .monocle-logo {
      transform: scale(0.7);
      padding: 0.5rem;
    }

    nav {
      min-width: 44rem;
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
      min-width: 38rem;
      min-height: 3.8rem;
    }
    nav a {
      padding-left: 0.4rem;
      padding-right: 0.4rem;
    }
  }
</style>
