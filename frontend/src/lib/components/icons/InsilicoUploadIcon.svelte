<script>
  import InsilicoIcon from "./InsilicoIcon.svelte";

  export let color = undefined;
  export let colorHover = undefined;
  export let height = 18;
  export let width = 18;
  export let style = undefined;
</script>


<svg aria-hidden="true" viewBox="0 0 18 18"
  {width}
  {height}
  style="fill: {color}; --color-hover: {colorHover}; {style}"
>
  <path fill-rule="evenodd" d="M8.53 1.22a.75.75 0 00-1.06 0L3.72 4.97a.75.75 0 001.06 1.06l2.47-2.47v6.69a.75.75 0 001.5 0V3.56l2.47 2.47a.75.75 0 101.06-1.06L8.53 1.22zM3.75 13a.75.75 0 000 1.5h8.5a.75.75 0 000-1.5h-8.5z">
  </path>
</svg>

<InsilicoIcon
  height={14}
  width={14}
  {color}
  style="position: absolute; left: 1.6rem; z-index: -1"
/>


<style>
svg:hover path {
  fill: var(--color-hover);
  transition: .1s;
}
</style>

