<script>
  import { EMAIL_MONOCLE_HELP } from "$lib/constants.js";
</script>

<footer>
  <div class="max-inner-width">
    <address>
      <div>Contacts</div>
      <a href={`mailto:${EMAIL_MONOCLE_HELP}`}>Monocle Help</a>
      <span aria-hidden="true">|</span>
      <a href="mailto:sdb@sanger.ac.uk">Stephen Bentley</a>
    </address>

    <a href="https://www.sanger.ac.uk/" target="_blank" class="sanger-link">
      <img alt="Wellcome Sanger Institute" src="/imgs/sangerlogowhite.svg" title="Wellcome Sanger Institute">
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
