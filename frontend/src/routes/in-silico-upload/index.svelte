<script>
  let files;
  let uploading;
</script>


<h2>In-silico data uploading</h2>

<p id="in-silico-uploading-description">Select or drag and drop your files with <em>in-silico</em> data:</p>

<form on:submit|preventDefault={() => {}} aria-labelledby="in-silico-uploading-description">
	<fieldset disabled={uploading}>
		<input
			bind:files
			type="file"
			multiple
		>
		
		<button type="submit" disabled={!files || files.length === 0}>
			Upload
		</button>
	</fieldset>
</form>


<style>
form, p {
  text-align: center;
}

fieldset {
  display: flex;
  flex-direction: column;
  align-items: center;
}

input[type=file] {
  margin: 1rem 0 2rem;
}
</style>
