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

This is a temporary bounded resolution. Any future vinext upgrade must rerun the
full audit and the site build before merge. A zero audit result does not replace
code review, secret scanning, runtime hardening, or an external security review.
