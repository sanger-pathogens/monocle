<script>
	export let midscreen = false;

	const style = midscreen ?
	  "position: absolute; transform: translateX(-50%); left: 50vw; top: 37vh" :
	  undefined;
</script>


<!-- The markup and CSS are based on https://codepen.io/Bidji/pen/emajjq -->
<div
	aria-label="please wait"
	aria-live="polite"
	class="cssload-wrap"
	{style}
>
	<div aria-hidden="true" class="cssload-container">
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
		<span class="cssload-dots"></span>
	</div>
</div>


<style>
.cssload-wrap {
	text-align: center;
	line-height: 62px;
	padding-bottom: 2rem;
}
	
.cssload-container {
	display: inline-block;
}

.cssload-dots {
	display: inline-block;
	position: relative;
}
.cssload-dots:not(:last-child) {
	margin-right: 9px;
}
.cssload-dots:before, .cssload-dots:after {
	content: "";
	display: inline-block;
	width: 6px;
	height: 6px;
	border-radius: 50%;
	position: absolute;
}
.cssload-dots:nth-child(1):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -0.9s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(1):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -0.9s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(2):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -1.8s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(2):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -1.8s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(3):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -2.7s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(3):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -2.7s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(4):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -3.6s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(4):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -3.6s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(5):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -4.5s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(5):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -4.5s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(6):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -5.4s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(6):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -5.4s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(7):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -6.3s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(7):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -6.3s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(8):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -7.2s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(8):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -7.2s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(9):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -8.1s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(9):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -8.1s;
	background-color: var(--juno-purple);
}
.cssload-dots:nth-child(10):before {
	transform: translateY(-200%);
	animation: cssload-animBefore 1s linear infinite;
	animation-delay: -9s;
	background-color: var(--juno-indigo);
}
.cssload-dots:nth-child(10):after {
	transform: translateY(200%);
	animation: cssload-animAfter 1s linear infinite;
	animation-delay: -9s;
	background-color: var(--juno-purple);
}




@keyframes cssload-animBefore {
	0% {
		transform: scale(1) translateY(-200%);
		z-index: 1;
	}
	25% {
		transform: scale(1.3) translateY(0);
		z-index: 1;
	}
	50% {
		transform: scale(1) translateY(200%);
		z-index: -1;
	}
	75% {
		transform: scale(0.7) translateY(0);
		z-index: -1;
	}
	100% {
		transform: scale(1) translateY(-200%);
		z-index: -1;
	}
}

@keyframes cssload-animAfter {
	0% {
		transform: scale(1) translateY(200%);
		z-index: -1;
	}
	25% {
		transform: scale(0.7) translateY(0);
		z-index: -1;
	}
	50% {
		transform: scale(1) translateY(-200%);
		z-index: 1;
	}
	75% {
		transform: scale(1.3) translateY(0);
		z-index: 1;
	}
	100% {
		transform: scale(1) translateY(200%);
		z-index: 1;
	}
}
</style>
