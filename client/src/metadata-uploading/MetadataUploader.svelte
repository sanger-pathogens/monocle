<script>
	import { createEventDispatcher } from "svelte";
	import LoadingIndicator from "../shared/components/LoadingIndicator.svelte";
	import ValidationErrorList from "./ValidationErrorList.svelte";

	const FILE_TYPE_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
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
					return response.json ? response.json() : Promise.reject(response.statusText);
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
		alert(
			`Upload error: ${err.message || err}.\nPlease try again and contact us if the problem persists.`
		);
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


<p id="uploading-description">Select or drag and drop your Excel files with sample metadata:</p>

<form on:submit|preventDefault={onFileSubmit} aria-labelledby="uploading-description">
	<fieldset disabled={uploading}>
		<input
			bind:files
			type="file"
			accept={FILE_TYPE_EXCEL}
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
/* FIXME: the CSS below is temporary: it'll be removed or updated once
the dashboard CSS is updated in https://trello.com/c/X66mRnj3/130-recreate-dashboard-in-javascript */
p {
	margin-bottom: 3rem;
}
form, p {
	text-align: center;
}
fieldset {
	display: inline-flex;
	flex-direction: column;
}
fieldset button, fieldset input {
	margin-bottom: 3rem;
}
</style>
