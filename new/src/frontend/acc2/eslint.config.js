import react from "eslint-plugin-react";
import prettier from "eslint-plugin-prettier";
import perfectionist from "eslint-plugin-perfectionist";
import unusedImports from "eslint-plugin-unused-imports";
import pluginQuery from "@tanstack/eslint-plugin-query";
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import reactCompiler from "eslint-plugin-react-compiler";
import tseslint from "typescript-eslint";
import tsParser from "@typescript-eslint/parser";
import path from "path";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default tseslint.config(
  { ignores: ["dist", "src/components/ui/**/*"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: globals.browser,
      parser: tsParser,
      sourceType: "module",

      parserOptions: {
        project: "./tsconfig.json",
      },
    },
    ...compat.extends(
      "eslint:recommended",
      "plugin:react/recommended",
      "plugin:@typescript-eslint/recommended"
    ),
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "unused-imports": unusedImports,
      "react-compiler": reactCompiler,
      "@tanstack/query": pluginQuery,
      react,
      prettier,
      perfectionist,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      ...pluginQuery.configs["flat/recommended"],
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-non-null-assertion": "error",

      "no-console": "warn",
      "no-await-in-loop": "warn",
      "no-param-reassign": "warn",
      "no-trailing-spaces": "warn",

      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIngorePattern: ",^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],

      "react/react-in-jsx-scope": "off",

      "perfectionist/sort-imports": [
        "error",
        {
          type: "alphabetical",
          order: "asc",
          ignoreCase: true,
          specialCharacters: "keep",
          internalPattern: ["^~/.+"],
          partitionByComment: false,
          partitionByNewLine: false,
          newlinesBetween: "always",
          maxLineLength: 120,
          groups: [
            "type",
            ["builtin", "external"],
            "internal-type",
            "internal",
            ["parent-type", "sibling-type", "index-type"],
            ["parent", "sibling", "index"],
            "object",
            "unknown",
          ],
          customGroups: { type: {}, value: {} },
          environment: "node",
        },
      ],
      "perfectionist/sort-named-imports": [
        "error",
        {
          type: "alphabetical",
          order: "asc",
          ignoreAlias: false,
          ignoreCase: true,
          specialCharacters: "keep",
          groupKind: "mixed",
          partitionByNewLine: false,
          partitionByComment: false,
        },
      ],

      "react-compiler/react-compiler": "warn",
    },
  }
);
