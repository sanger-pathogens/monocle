<script context="module">
  const TITLE = "Upload";
</script>

<script>
  import Icon from "./_Icon.svelte";

  export let color = undefined;
  export let colorHover = undefined;
  export let focusable = false;
  export let style = undefined;
  export let cssClass = undefined;
</script>

<Icon
  height="27"
  width="27"
  heightViewBox="20"
  widthViewBox="20"
  {color}
  {colorHover}
  {focusable}
  {cssClass}
  {style}
>
  <!-- The <g> container is needed because <title> isn't displayed as a tooltip if it's a direct descendant of <svg>. -->
  <g>
    <title>{TITLE}</title>
    <path
      fill-rule="evenodd"
      d="M8.53 1.22a.75.75 0 00-1.06 0L3.72 4.97a.75.75 0 001.06 1.06l2.47-2.47v6.69a.75.75 0 001.5 0V3.56l2.47 2.47a.75.75 0 101.06-1.06L8.53 1.22zM3.75 13a.75.75 0 000 1.5h8.5a.75.75 0 000-1.5h-8.5z"
    />
    <path d="M7,10L12,15L17,10H7Z" transform="translate(7,9.5) scale(0.65)" />
  </g></Icon
>
