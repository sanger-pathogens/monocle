import nodeAdapter from "@sveltejs/adapter-node";

const production = process.env.NODE_ENV === "production" || process.env.NODE_ENV === undefined;

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // hydrate the <div id="app"> element in src/app.html
    target: "#app",
    // `appDir` should be the same as the route in `proxy/nginx.prod.proxy.conf`:
    appDir: "_app",
    ssr: production,
    adapter: nodeAdapter({
      precompress: production
    })
  }
};

export default config;
