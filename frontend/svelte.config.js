import nodeAdapter from '@sveltejs/adapter-node';

const production = !process.env.ROLLUP_WATCH;

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // hydrate the <div id="app"> element in src/app.html
    target: '#app',
    adapter: nodeAdapter({
      precompress: production
	})
  }
};

export default config;
