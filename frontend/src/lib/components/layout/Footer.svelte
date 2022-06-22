<script>
  export let session;
</script>

<footer>
  <div class="max-inner-width">
    <address>
      <div>Contacts</div>
      {#if $session?.project?.contacts}
        {#each $session.project.contacts as contact}
          <a class="contact" href={contact.url}>{contact.label}</a>
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

  a.contact:not(:last-of-type)::after {
    content: "|";
    margin-left: 0.4rem;
    margin-right: 0.4rem;
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
