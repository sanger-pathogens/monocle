<script>
  import Icon from "./_Icon.svelte";

  export let color = undefined;
  export let height = 18;
  export let width = 18;
</script>

<Icon {color} {height} {width} heightViewBox="24" widthViewBox="24">
  <path
    d="M11 11L16.76 3.62A1 1 0 0 0 16.59 2.22A1 1 0 0 0 16 2H2A1 1 0 0 0 1.38 2.22A1 1 0 0 0 1.21 3.62L7 11V16.87A1 1 0 0 0 7.29 17.7L9.29 19.7A1 1 0 0 0 10.7 19.7A1 1 0 0 0 11 18.87V11M13 16L18 21L23 16Z"
  />
</Icon>
