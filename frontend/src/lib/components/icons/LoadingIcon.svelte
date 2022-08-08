<script>
  import Icon from "./_Icon.svelte";

  export let label = undefined;
  export let style = undefined;
</script>

<Icon
  {label}
  color="silver"
  heightViewBox="24"
  widthViewBox="24"
  cssClass="spinner"
  {style}
>
  <path fill="none" d="M0 0h24v24H0z" />
  <path d="M18.364 5.636L16.95 7.05A7 7 0 1 0 19 12h2a9 9 0 1 1-2.636-6.364z" />
</Icon>

<style>
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(359deg);
    }
  }
  :global(.spinner) {
    animation: spin 1.5s linear infinite;
    position: relative;
    top: 0.1rem;
  }
</style>
