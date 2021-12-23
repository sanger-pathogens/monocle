<svg aria-hidden="true" class="spinner" fill="#686868" viewBox="0 0 24 24" width="18" height="18">
  <path fill="none" d="M0 0h24v24H0z"/>
  <path d="M18.364 5.636L16.95 7.05A7 7 0 1 0 19 12h2a9 9 0 1 1-2.636-6.364z"/>
</svg>


<style>
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(359deg); }
}
.spinner {
  animation: spin 1.5s linear infinite;
  position: relative;
  top: .1rem;
}
</style>
