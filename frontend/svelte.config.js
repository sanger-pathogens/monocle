import nodeAdapter from "@sveltejs/adapter-node";

const production = process.env.NODE_ENV === "production" || process.env.NODE_ENV === undefined;

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // `appDir` should be the same as the route in `proxy/nginx.prod.proxy.conf`:
    appDir: "_app",
    adapter: nodeAdapter({
      precompress: production
    })
  }
};

export default config;
