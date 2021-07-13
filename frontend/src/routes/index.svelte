<script context="module">
	// This function loads the data expected by the component, before the component is created.
	// It can run both during server-side rendering and in the client. See https://kit.svelte.dev/docs#loading.
	export function load({ fetch }) {
		// FIXME: this is only a hardcoded payload from http://monocle.dev.pam.sanger.ac.uk/legacy_dashboard/data/summary/
		const { institution_status: institutionStatus, progress_graph: projectProgress } =
			{"institution_select":{"institutions":{"FacPhaSueCanUni":{"db_key":"Faculty of Pharmacy, Suez Canal University","name":"Faculty of Pharmacy, Suez Canal University"},"LabCenEstPar":{"db_key":"Laborat\u00f3rio Central do Estado do Paran\u00e1","name":"Laborat\u00f3rio Central do Estado do Paran\u00e1"},"NatRefLab":{"db_key":"National Reference Laboratories","name":"National Reference Laboratories"},"TheChiUniHonKon":{"db_key":"The Chinese University of Hong Kong","name":"The Chinese University of Hong Kong"},"UniFedRioJan":{"db_key":"Universidade Federal do Rio de Janeiro","name":"Universidade Federal do Rio de Janeiro"},"WelSanIns":{"db_key":"Wellcome Sanger Institute","name":"Wellcome Sanger Institute"}}},"institution_status":{"batches":{"FacPhaSueCanUni":{"deliveries":[{"date":"2020-10-05","name":"Batch 1","number":90}],"expected":90,"received":90},"LabCenEstPar":{"deliveries":[{"date":"2019-09-18","name":"Batch 1","number":1},{"date":"2021-03-15","name":"Batch 2","number":24}],"expected":25,"received":25},"NatRefLab":{"deliveries":[{"date":"2019-11-15","name":"Batch 1","number":100}],"expected":100,"received":100},"TheChiUniHonKon":{"deliveries":[{"date":"2019-09-18","name":"Batch 1","number":251}],"expected":251,"received":251},"UniFedRioJan":{"deliveries":[{"date":"2021-03-15","name":"Batch 1","number":456}],"expected":456,"received":456},"WelSanIns":{"deliveries":[],"expected":0,"received":0}},"institutions":{"FacPhaSueCanUni":{"db_key":"Faculty of Pharmacy, Suez Canal University","name":"Faculty of Pharmacy, Suez Canal University"},"LabCenEstPar":{"db_key":"Laborat\u00f3rio Central do Estado do Paran\u00e1","name":"Laborat\u00f3rio Central do Estado do Paran\u00e1"},"NatRefLab":{"db_key":"National Reference Laboratories","name":"National Reference Laboratories"},"TheChiUniHonKon":{"db_key":"The Chinese University of Hong Kong","name":"The Chinese University of Hong Kong"},"UniFedRioJan":{"db_key":"Universidade Federal do Rio de Janeiro","name":"Universidade Federal do Rio de Janeiro"},"WelSanIns":{"db_key":"Wellcome Sanger Institute","name":"Wellcome Sanger Institute"}},"pipeline_status":{"FacPhaSueCanUni":{"completed":90,"fail_messages":[{"lane":"L123423354","stage":"preprocessing","issue":"A dog ate punch cards. (The dog is fine.)"},{"lane":"L23456","stage":"reception","issue":"Samples were taken by hyperdimensional beings. The HD department is working on tracing the samples."}],"failed":2,"running":0,"success":88},"LabCenEstPar":{"completed":1,"fail_messages":[],"failed":0,"running":0,"success":1},"NatRefLab":{"completed":100,"fail_messages":[{"lane":"L101101100","stage":"arm-chairing","issue":"There are only problems and (in)effective ways of addressing them."}],"failed":1,"running":0,"success":99},"TheChiUniHonKon":{"completed":250,"fail_messages":[],"failed":0,"running":0,"success":250},"UniFedRioJan":{"completed":0,"fail_messages":[],"failed":0,"running":0,"success":0},"WelSanIns":{"completed":0,"fail_messages":[],"failed":0,"running":0,"success":0}},"sequencing_status":{"FacPhaSueCanUni":{"completed":92,"fail_messages":[{"lane":"L123423354","stage":"preprocessing","issue":"A dog ate punch cards. (The dog is fine.)"},{"lane":"L23456","stage":"reception","issue":"Samples were taken by hyperdimensional beings. The HD department is working on tracing the samples."}],"failed":2,"received":92,"success":90},"LabCenEstPar":{"completed":1,"fail_messages":[],"failed":0,"received":25,"success":1},"NatRefLab":{"completed":101,"fail_messages":[{"lane":"L101101100","stage":"arm-chairing","issue":"There are only problems and (in)effective ways of addressing them."}],"failed":1,"received":101,"success":100},"TheChiUniHonKon":{"completed":250,"fail_messages":[],"failed":0,"received":251,"success":250},"UniFedRioJan":{"completed":0,"fail_messages":[],"failed":0,"received":456,"success":0},"WelSanIns":{"completed":0,"fail_messages":[],"failed":0,"received":0,"success":0}}},"progress_graph":{"data":{"date":["Sep 2019","Oct 2019","Nov 2019","Dec 2019","Jan 2020","Feb 2020","Mar 2020","Apr 2020","May 2020","Jun 2020","Jul 2020","Aug 2020","Sep 2020","Oct 2020","Nov 2020","Dec 2020","Jan 2021","Feb 2021","Mar 2021", "Apr 2021", "May 2021", "Jun 2021", "Jul 2021"],"samples received":[252,252,352,352,352,352,352,352,352,352,352,352,352,442,442,442,442,442,922,922,922,922,922],"samples sequenced":[0,0,251,251,351,351,351,351,351,351,351,351,351,351,441,441,441,441,441,441,441,441]},"title":"Project Progress","x_col_key":"date","x_label":"","y_cols_keys":["samples received","samples sequenced"],"y_label":"number of samples"}};

		return {
			props: {
				institutions: collateInstitutionStatus(institutionStatus),
				projectProgress: {
					dates: projectProgress.data.date,
					datasets: [{
						name: "samples received",
						values: projectProgress.data["samples received"]
					}, {
						name: "samples sequenced",
						values: projectProgress.data["samples sequenced"]
					}]
				}
			}
		};
	}

	function collateInstitutionStatus({
		institutions,
		batches,
		sequencing_status,
		pipeline_status
	}) {
		return Object.keys(institutions)
			.map((key) => ({
				name: institutions[key].name,
				batches: batches[key],
				sequencingStatus: sequencing_status[key],
				pipelineStatus: {
					sequencedSuccess: sequencing_status[key].success,
					...pipeline_status[key]
				},
				key
			}))
	}
</script>

<script>
  import InstitutionStatus from './_dashboard/_InstitutionStatus.svelte';
  import LineChart from '$lib/components/LineChart.svelte';

  export let institutions;
  export let projectProgress = {};
</script>


<LineChart
	title="Project Progress"
  datasets={projectProgress.datasets}
  labels={projectProgress.dates}
/>

{#each institutions as { name, batches, sequencingStatus, pipelineStatus, key } (key)}
	<InstitutionStatus
		{batches}
		{sequencingStatus}
		{pipelineStatus}
		institutionName={name}
	/>
{:else}
	<p>No institutions found for this account. This may be an error, so please try to reload the page or to log out and log in again.</p>
{/each}
