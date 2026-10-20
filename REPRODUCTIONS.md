# Reproduction reports

Run the [README command](README.md) and report failures as well as passes using
the [Reproduction report issue form](https://github.com/Silentpartnercoding/minority-prophet/issues/new?template=reproduction.yml).
The [check contract](docs/CHECK.md) states the exact scope and failure conditions.

Record:

- Name or public handle; organization optional.
- UTC date, full commit SHA, and clean/modified worktree state.
- OS/architecture, Python version, and exact command.
- Complete output and process exit code, including failures.
- Whether this was the supplied demo, a Lean build/axiom audit, or a separately
  written implementation; describe any changes and reused code.
- Relationship to the project/operator and which independence claims remain
  unestablished. A different account or machine alone does not establish independence.

For a report tied to a particular revision, check out its full SHA before running
`make demo`. To save output outside the checkout and retain its exit status:

```bash
make demo > /tmp/mp-demo-output.txt 2>&1
status=$?
cat /tmp/mp-demo-output.txt
printf 'exit_code=%s\n' "$status"
```

Use a clean checkout for an exact-commit reproduction. A modified tree is useful
for debugging, but its SHA alone does not identify everything executed. Include
a public patch or fork commit for changes. Do not include credentials or private data.

## One authoritative registry

Accepted external evidence is recorded in
[`EXTERNAL-REPRODUCTIONS.json`](research/knowledge-ledger/EXTERNAL-REPRODUCTIONS.json),
with its artifact pin, source report, evidence strength, and explicit limits.
This page is intake/navigation, not a second result ledger. Issue submission alone
does not establish an accepted result or organizational independence.

The existing entries concern other artifacts and do not discharge the MP core
claim. The historical Christopher He verification credit requires reconciliation
with a source report before it can be classified as an accepted external
reproduction; see [the evidence note](docs/evidence/REPRODUCTION-STATUS.md).

Maintainers should link a qualifying report from the README only with its name,
date, commit, and exact reproduced scope. Internal runs by agents sharing this
project's operator are internal replication.
