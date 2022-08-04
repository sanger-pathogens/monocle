<script context="module">
  // Variables inside <script> w/ `context="module" are defined only once and shared between each component instance.
  const COLOR_DEFAULT = "var(--text-main)";
  const TAB_INDEX_FOCUSABLE = "0";
  const VIEWBOX_HEIGHT_DEFAULT = "18";
  const VIEWBOX_WIDTH_DEFAULT = "18";
</script>

<script>
  let styleProp = "";
  export let label = undefined;
  export let color = COLOR_DEFAULT;
  export let colorHover = undefined;
  export let cssClass = undefined;
  export let height = 18;
  export let width = 18;
  export let heightViewBox = VIEWBOX_HEIGHT_DEFAULT;
  export let widthViewBox = VIEWBOX_WIDTH_DEFAULT;
  export let focusable = false;
  export { styleProp as style };

  $: style = combineStyle(colorHover, styleProp);

  function combineStyle(colorHoverArg, restStyle) {
    const styleCombined = colorHoverArg
      ? `--color-hover:${colorHoverArg};`
      : "";
    return (restStyle ? `${styleCombined}${restStyle}` : styleCombined).trim();
  }
</script>

<svg
  aria-hidden={label ? null : "true"}
  viewBox="0 0 {widthViewBox} {heightViewBox}"
  {width}
  {height}
  class={cssClass}
  class:hoverable={Boolean(colorHover)}
  fill={color}
  style={style || null}
  tabindex={focusable ? TAB_INDEX_FOCUSABLE : null}
>
  {#if label}
    <title>{label}</title>
  {/if}
  <slot />
</svg>

<style>
  /* Since <path> is outside the styling scope of this component, we need to use `:global()` to reach it
  (h/t https://stackoverflow.com/a/46094511/4579279): */
  .hoverable:hover :global(path) {
    fill: var(--color-hover);
    transition: 0.1s;
  }
</style>
