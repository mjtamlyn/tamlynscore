import { defineConfig, globalIgnores } from "eslint/config";
import react from "eslint-plugin-react";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default defineConfig([
    globalIgnores([
        "./bundles",
        "./htmlcov",
        "./eslint.config.mjs",
        "./webpack.config.js",
        "./core/static",
        "./entries/static",
        "./scores/static",
        "./tamlynscore/static/lib",
        "./tamlynscore/static/js",
    ]),
    {
        extends: compat.extends("eslint:recommended", "plugin:react/recommended"),

        plugins: { react },
        settings: { react: { "version": "detect", } },
        languageOptions: {
            globals: {
                ...globals.browser,
                Atomics: "readonly",
                SharedArrayBuffer: "readonly",
            },

            ecmaVersion: 2018,
            sourceType: "module",
        },

        rules: {
            "react/prop-types": 0,
        },
    },
]);
