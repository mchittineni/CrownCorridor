module.exports = [
  {
    files: ["app/**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "module",
      globals: {
        window: "readonly",
        document: "readonly",
        console: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        URLSearchParams: "readonly",
        alert: "readonly",
        L: "readonly",
        Chart: "readonly",
        pmtiles: "readonly",
        maplibregl: "readonly",
        portal: "writable"
      }
    },
    rules: {
      indent: "off",
      quotes: ["error", "single", { avoidEscape: true, allowTemplateLiterals: true }],
      semi: ["error", "always"],
      "no-unused-vars": ["warn", { args: "none" }],
      "no-console": "off",
      eqeqeq: ["error", "always"],
      curly: ["error", "multi-line"]
    }
  }
];
