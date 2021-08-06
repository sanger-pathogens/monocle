<script>
  import { createEventDispatcher } from "svelte";
  import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
  import ValidationErrorList from "./_ValidationErrorList.svelte";

  const FILE_TYPE_CSV = ".csv,text/csv";
  const UPLOAD_API_URL = "/metadata/upload";

  export let files = [];

  const dispatch = createEventDispatcher();
  let uploading = false;
  let validationErrors = [];

  function onFileSubmit() {
    uploading = true;

    uploadFiles(emitUploadSuccess)
      .catch(onUploadError)
      .finally(() => {
        uploading = false;
      });
    }

  function uploadFiles(successCallback) {
    const filesArray = Array.from(files);
    const uploadRequests = filesArray.map((file) => uploadFile(file));
    return Promise.all(uploadRequests)
      .then((results) => {
        hasValidationErrors(results) ?
          handleValidationErrors(results, filesArray) :
          successCallback();
      });
  }

  function uploadFile(file) {
    const formData = new FormData();
    formData.append("spreadsheet", file);
    return fetch(UPLOAD_API_URL, {
      method: "POST",
      body: formData
    })
      .then((response) => {
        if (!response.ok) {
          return response.json ?
            response.json()
              .catch((err) => {
                console.log(`JSON parsing error: ${err}`);
                return Promise.reject(response.statusText);
              })
            : Promise.reject(response.statusText);
        }
      });
  }

  function emitUploadSuccess() {
    dispatch("uploadSuccess");
  }

  function handleValidationErrors(errors, files) {
    validationErrors = mapFilesToValidationErrors(errors, files);
  }

  function onUploadError(err) {
    const uploadError = err ? (`Upload error: ${err.message || err}`) : "Upload error";
    alert(`${uploadError}\nPlease try again and contact us if the problem persists.`);
  }

  function hasValidationErrors(errors) {
    return errors.some((error) => error !== undefined);
  }

  function mapFilesToValidationErrors(errors, files) {
    return errors.reduce(
      (accum, error = {}, i) => {
        if (typeof error === "string" || error.errors) {
          accum.push({
            fileName: files[i].name,
            errorMessages: error.errors || [error]
          });
        }
        return accum;
      },
      []
    );
  }
</script>


<p id="uploading-description">Select or drag and drop your files with tab-separated sample metadata (<code>.tab</code>, <code>.tsv</code>, and <code>.txt</code> extensions are supported):</p>

<form on:submit|preventDefault={onFileSubmit} aria-labelledby="uploading-description">
	<fieldset disabled={uploading}>
		<input
			bind:files
			type="file"
			accept={FILE_TYPE_CSV}
			multiple
		>
		
		<button type="submit" disabled={files.length === 0}>
			Upload
		</button>
	</fieldset>
</form>

{#if uploading}
	<LoadingIndicator />
{/if}

{#if validationErrors.length}
	<ValidationErrorList errors={validationErrors} />
{/if}


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
