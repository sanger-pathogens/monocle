<script>
  import { fade } from "svelte/transition";

  export let ariaLabel = undefined;
  export let ariaLabelledby = undefined;
  export let isOpen = false;
  export let persistState = false;

  let dialogBackground;

  function close() {
    isOpen = false;
  }
</script>


{#if persistState || isOpen}
  <!-- To persist state of the dialog we need to hide it w/ the inline `style` below, instead of simply not rendering it. -->
  <div
    role="dialog"
    aria-label={ariaLabel}
    aria-labelledby={ariaLabelledby}
    style:display={persistState && !isOpen ? "none" : null}
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
  background: rgba(250, 250, 250, .7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9;
}

.content {
  background: #fff;
  border-radius: 3px;
  box-shadow: 0 .2rem .4rem rgba(48 ,55 ,66, .3);
  max-height: 85vh;
  overflow-y: auto;
  max-width: 40rem;
  padding: 1.2rem;
  position: relative;
}

.close-icon-btn {
  position: absolute;
  top: .3rem;
  right: .6rem;
  border: none;
  color: gray;
  font-size: 1.2rem;
  padding: .2rem .5rem;
}
.close-icon-btn:hover {
  color: black;
}
.close-icon-btn:before {
  /* Cross for the close button */
  content: "\2715";
}
</style>

