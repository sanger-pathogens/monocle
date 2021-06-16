<script>
	import Header from "./Header.svelte";
	import Footer from "./Footer.svelte";
	import MetadataUploader from "./metadata-uploading/MetadataUploader.svelte";
	
	export let injectedWindow = window;

	function redirectToDashboard() {
		injectedWindow.location.assign("/dashboard");
	}
</script>


<Header />

<main>
	<h2>Metadata uploading</h2>
	<MetadataUploader on:uploadSuccess={redirectToDashboard} />
</main>

<Footer />


<style>
:global(:root) {
	--juno-indigo: #484885;
	--juno-purple: #6868be;
}

/* FIXME: the CSS below is temporary: it'll be removed or updated once
the dashboard CSS is updated in https://trello.com/c/X66mRnj3/130-recreate-dashboard-in-javascript */
main {
	align-self: center;
	flex-grow: 1;
	display: flex;
	flex-direction: column;
	width: 70rem;
	max-width: 100%
}
h2 {
	margin-bottom: 4rem;
	text-align: center;
}
</style>
