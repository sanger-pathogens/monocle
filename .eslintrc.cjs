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
    "no-promise-executor-return": ERROR,
    "no-return-await": ERROR,
    "no-shadow": ERROR,
    "no-unused-expressions": ERROR,
    "no-useless-concat": ERROR,
    "no-useless-return": ERROR,
    "prefer-const": ERROR,
    "prefer-rest-params": ERROR,
    "require-await": ERROR,
    // Code style rules:
    camelcase: ERROR,
    "dot-notation": ERROR,
    yoda: ERROR,
  },
  settings: {
    jest: {
      version: require("./frontend/package.json").devDependencies.jest,
    },
  },
};
