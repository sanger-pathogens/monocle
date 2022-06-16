<script>
  export let session;
</script>

<footer>
  <div class="max-inner-width">
    <address>
      <div>Contacts</div>
      {#if typeof $session.project !== "undefined" && typeof $session.project.name !== "undefined"}
        {#each $session.project.contacts as contact, num}
          {#if num > 0}
            <span aria-hidden="true">&nbsp;|</span>
          {/if}
          <a href={contact.url}>{contact.label}</a>
        {/each}
      {/if}
    </address>

    <a href="https://www.sanger.ac.uk/" target="_blank" class="sanger-link">
      <img
        alt="Wellcome Sanger Institute"
        src="/imgs/sangerlogowhite.svg"
        title="Wellcome Sanger Institute"
      />
    </a>
  </div>
</footer>

<style>
  footer {
    display: flex;
    justify-content: space-around;
    background: var(--juno-purple);
    color: white;
    margin-top: auto;
    padding: 1.4rem 1.4rem 1.8rem;
  }

  .max-inner-width {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    max-width: var(--bp-xl);
    width: 100%;
  }

  a {
    color: white;
  }

  .sanger-link {
    order: -1;
    margin-right: auto;
    padding-right: 0.6rem;
  }
  .sanger-link img {
    width: 7.3rem;
  }

  address {
    text-align: right;
  }

  address div:first-child {
    font-style: italic;
    text-align: right;
  }
</style>
