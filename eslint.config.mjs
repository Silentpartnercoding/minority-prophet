import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "formal/lean/.lake/**",
    "next-env.d.ts",
    // Sibling clones that live inside this working tree. They are separate
    // repositories, not part of this one, and CI never sees them because they
    // are untracked. Locally they made `make verify-site` fail with thousands
    // of problems from other projects' code. Ignored for the same reason they
    // are in .gitignore.
    "mp-decision-relative/**",
    "mp-dri1b-human-site/**",
    "mp-dri1b-prereg/**",
    "mp-home-source-family/**",
  ]),
]);

export default eslintConfig;
