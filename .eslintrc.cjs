module.exports = {
  env: {
    browser: true,
    es2022: true,
    node: true,
    "jest/globals": true,
  },
  extends: ["eslint:recommended", "plugin:jest/recommended", "prettier"],
  parserOptions: {
    sourceType: "module",
  },
  plugins: ["jest", "svelte3"],
  overrides: [
    {
      files: ["*.svelte"],
      processor: "svelte3/svelte3",
    },
  ],
  rules: {
    eqeqeq: "error",
    "jest/expect-expect": [
      "error",
      {
        assertFunctionNames: ["expect*"],
      },
    ],
  },
  settings: {
    jest: {
      version: require("./frontend/package.json").devDependencies.jest,
    },
  },
};
