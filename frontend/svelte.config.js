import nodeAdapter from "@sveltejs/adapter-node";

const production =
  process.env.NODE_ENV === "production" || process.env.NODE_ENV === undefined;

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: nodeAdapter({
      precompress: production,
    }),
  },
};

export default config;
