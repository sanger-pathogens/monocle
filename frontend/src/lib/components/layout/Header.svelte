<header>
  <h1><a href="/">Monocle</a></h1>
  <nav>
    <a href="https://www.gbsgen.net/" target="_blank" class="juno-link">
      <img alt="Juno Project" src="/imgs/junologo.svg" title="Juno Project">
    </a>
    <a href="https://www.gbsgen.net/#about" target="_blank">About</a>
    <a href="https://www.gbsgen.net/#team" target="_blank">Team</a>
    <a href="https://www.gbsgen.net/#partners" target="_blank">Partners</a>
    <a href="https://www.gbsgen.net/#twitterFeed" target="_blank">News</a>
    <a href="https://www.gbsgen.net/#funders" target="_blank">Funders</a>
  </nav>
</header>


<style>
header {
  background: var(--juno-purple);
  padding: 1rem 1.2rem;
  position: relative;
  min-height: 4rem;
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
@media (max-width: 940px) {
  h1 {
    font-size: 2rem;
    margin-bottom: 0;
    position: initial;
    text-align: center;
    transform: none;
  }
}

a {
  color: white;
}

nav {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  margin: auto;
  max-wigth: var(--bp-xl);
}

nav a {
  padding: 0.6rem;
}

.juno-link {
  margin-right: auto;
}
.juno-link img {
  width: 4rem;
}
</style>
