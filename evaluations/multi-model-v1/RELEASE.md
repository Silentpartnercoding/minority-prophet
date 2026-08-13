# Runtime release evidence

Build a local, unpublished release candidate with:

```sh
npm run pack:evidence
```

The command recreates `dist/runtime-release`, runs `npm pack`, refuses any file
outside the runtime package allowlist, refuses a dirty source tree, and writes:

- the npm archive;
- `SHA256SUMS`;
- `release-evidence.json`, bound to the exact source commit;
- `sbom.spdx.json` using SPDX 2.3.

This is release evidence, not publication or signing. Registry publication,
GitHub provenance attestation, tag creation, and use of a signing identity remain
owner-authorized release actions. Do not sign a dirty tree or substitute an
archive after generating its evidence.
