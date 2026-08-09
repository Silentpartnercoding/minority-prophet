# Graduated research integrity

Ordinary contributions remain ordinary. The additional lifecycle check applies
when work is promoted into a candidate, canonical record, imported result, or a
new top-level `results/` directory.

Each enrolled record owns one file under `research/records/`. Per-record files
let many agents work without contending on a central mutable registry.

- `exploratory`: no preregistration required; cannot claim canonical status;
- `candidate`: requires a content-bound protocol and no confirmation result;
- `canonical`: requires a previously recorded candidate, a strictly earlier
  protocol commit, result, manifest, honest verdict, and immutable record;
- `imported`: requires content-bound imported protocol/result/manifest material
  and explicit control relationship; it is not a repository-native rerun.

All stages require `authorityEffect: "none"`. An `independent` assessment also
requires a content-bound witness explicitly recorded as externally controlled.
This validates the declared evidence package; it cannot discover hidden common
control.

See `research-record.schema.json` and run:

```text
make verify
```

Create records with `python scripts/new_research_record.py --help`; the command
computes hashes, resolves commits, refuses unsafe overwrites, and requires a
candidate to predate its canonical result. Validation failures print a `Fix:`
line with the narrow remediation. The checker never edits evidence on behalf of
the contributor.
