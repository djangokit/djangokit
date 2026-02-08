import globals from "globals";
import js from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import prettierRecommended from "eslint-plugin-prettier/recommended";

export default defineConfig(
  globalIgnores([
    "**/ansible/",
    "**/build/",
    "**/dist/",
    "**/static/lib",
    "**/__pycache__/",
    "**/.venv/",
  ]),
  [
    {
      files: ["**/*.{js,mjs}"],

      plugins: {
        js,
      },

      extends: ["js/recommended"],

      languageOptions: {
        globals: globals.browser,
      },
    },

    js.configs.recommended,
    prettierRecommended,
  ],
);
