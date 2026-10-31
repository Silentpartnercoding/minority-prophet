# Dependency security status

This is a Routine maintenance record, not an assertion that the application or
deployment is vulnerability-free.

On 2026-08-13 the locked dependency tree was changed in two bounded ways:

- `nanoid` moved from 3.3.17 to 3.3.18, removing its published high-severity
  advisory from the production dependency audit;
- `vinext` moved from 0.0.50 to 0.0.45. The newer version introduced
  `image-size@2.0.2`, whose published parser denial-of-service advisories had no
  patched npm release. The selected version does not depend on `image-size`.

After the change, `npm audit` reports zero known vulnerabilities and the complete
site build and rendered-page tests pass. CI now runs the full audit, not only the
production-dependency subset.

On 2026-10-15, runtime dependencies were advanced to remove new `sharp` and
`source-map-js` advisories. The remaining audit graph traces only to
`GHSA-vfj7-8cjw-p6xm` in `braces`, for which npm publishes no patched release.
It is reachable through development-only glob consumers (`eslint-config-next`
and `vinext`), not through the deployed production dependency set; `npm audit
--omit=dev` reports zero findings. CI still audits the full tree and permits only
that exact advisory and dependency chain. Any different advisory fails the build.

On 2026-10-30, `@vercel/og` and `fflate` overrides moved `satori` to the patched
0.33.5. The same day `GHSA-g3hv-75wg-m249` was published for `minimatch` below
11.0.1. It is reached only through development lint tooling (`eslint`,
`eslint-config-next` and their plugins) and is not used at runtime; `npm audit
--omit=dev` reports zero findings. No compatible patched 3.x release exists, so
CI permits that exact advisory too. Revisit when eslint ships a fix.

This is a temporary bounded resolution. Any future vinext upgrade must rerun the
full audit and the site build before merge. A zero audit result does not replace
code review, secret scanning, runtime hardening, or an external security review.
