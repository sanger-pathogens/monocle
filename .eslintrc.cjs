const ERROR = "error";

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
    "jest/expect-expect": [
      ERROR,
      {
        assertFunctionNames: ["expect*"],
      },
    ],
    eqeqeq: ERROR,
    "no-param-reassign": ERROR,
    "no-return-await": ERROR,
    "no-shadow": ERROR,
    "no-unused-expressions": [
      ERROR,
      {
        allowShortCircuit: true,
        allowTernary: true,
      },
    ],
    "no-useless-concat": ERROR,
    "no-useless-return": ERROR,
    "prefer-const": ERROR,
    "prefer-rest-params": ERROR,
    // Code style rules:
    // FIXME: enforce camelcase as well:
    // "camelcase": ERROR,
    "dot-notation": ERROR,
    "id-length": ERROR,
    yoda: ERROR,
  },
  settings: {
    jest: {
      version: require("./frontend/package.json").devDependencies.jest,
    },
  },
};
