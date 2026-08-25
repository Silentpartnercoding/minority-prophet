# Contributor map

Contributions are welcome, but the correct path depends on whether a change is
ordinary engineering or a claim-bearing research change.

## Start here

1. Read [`CONTRIBUTOR-QUICKSTART.md`](../../CONTRIBUTOR-QUICKSTART.md).
2. Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md) and choose the documented
   contribution lane.
3. Read [`AGENTS.md`](../../AGENTS.md) if an automated coding agent will work in
   the repository.
4. Run `make setup`, then `make verify` before handoff.

## Ordinary changes

Documentation navigation, isolated fixes, test improvements, and other
non-claim-bearing work use the ordinary contribution lane. Do not create a
research record merely because a patch touches research code.

## Claim-bearing research

Promotion to candidate, canonical, imported, or a new top-level result package
uses the graduated lifecycle in
[`research/integrity/README.md`](../../research/integrity/README.md). Create a
record with:

```bash
python scripts/new_research_record.py --help
```

The checks validate declared evidence packages; they do not discover hidden
common control or certify independence.

## Pull-request hygiene

- Keep one purpose per pull request.
- Preserve negative, incomplete, and superseded evidence.
- Do not rewrite canonical/imported records in place.
- Link claims to exact records and distinguish measured results from proposals.
- Add or update tests when behavior changes.
- Avoid mixing site copy, research promotion, and runtime behavior unless the
  change genuinely requires all three.

For project terminology, see [`GLOSSARY.md`](../../GLOSSARY.md). For the public
claim boundary, see [`PUBLIC-CLAIMS.md`](../../PUBLIC-CLAIMS.md).
