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
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
});

export default tseslint.config(
  {
    ignores: [
      "dist",
      "src/components/ui/**/*",
      ".vite",
      "tailwind.config.js",
      "vite.config.ts",
      "src/vite-env.d.ts",
    ],
  },

  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginQuery.configs["flat/recommended"],
  ...compat.extends("plugin:react/recommended"),

  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: globals.browser,
      parser: tsParser,
      sourceType: "module",
      parserOptions: {
        project: ["./tsconfig.json"],
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "unused-imports": unusedImports,
      "react-compiler": reactCompiler,
      react,
      prettier,
      perfectionist,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,

      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],

      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],

      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-non-null-assertion": "error",

      "no-console": "warn",
      "no-await-in-loop": "warn",
      "no-param-reassign": "warn",
      "no-trailing-spaces": "warn",

      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",

      "perfectionist/sort-imports": ["error", {}],
      "perfectionist/sort-named-imports": ["error", {}],

      "react-compiler/react-compiler": "warn",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  }
);
