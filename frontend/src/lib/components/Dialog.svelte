<script>
  import { fade } from "svelte/transition";

  export let isOpen = false;

  let dialogBackground;

  function close() {
    isOpen = false;
  }
</script>


{#if isOpen}
  <div
    role="dialog"
    bind:this={dialogBackground}
    on:click={(event) => event.target === dialogBackground && close()}
    in:fade={{ duration: 90 }}
  >
    <div class="content">
      <button
        aria-label="Close dialog"
        on:click={close}
        class="close-icon-btn"
      ></button>
      <slot></slot>
    </div>
  </div>
{/if}


<style>
[role=dialog] {
  /* `position: fixed` will break if any ancestor element has `transform` property. */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9;
}

.content {
  background: #fff;
  border-radius: 3px;
  max-height: 98vh;
  overflow-y: auto;
  max-width: 40rem;
  padding: 1rem;
  position: relative;
}

.close-icon-btn {
  position: absolute;
  top: .2rem;
  right: .4rem;
  background: rgba(0, 0, 0, 0);
  border-radius: 50%;
  color: gray;
  font-size: .9rem;
  margin: 0;
  padding: 0;
  height: 1.25rem;
  width: 1.25rem;
}
.close-icon-btn:hover {
  color: black;
}
.close-icon-btn:before {
  /* Cross for the close button */
  content: "\2715";
}
</style>

