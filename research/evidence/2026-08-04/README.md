# Research evidence release — 2026-08-04

This branch preserves the current research packet as **paper-draft and
replica/design-validation evidence**. It does not promote Experiments
003–008 to canonical status.

## Included

- `../../../papers/MINORITY-PROPHET-PAPER-v0.9.md` — latest draft paper.
- `../../../experiments/exp008_shootout.py` — portable EXP008 reference
  shootout, comparing majority voting, Dawid–Skene, TruthFinder, ACCU-lite,
  clustering, inferred-root counting, and declared-root counting.
- `archives/minority-prophet-handoff.zip` — EXP003–005 handoff, reference
  implementations, raw outputs, plots, and its embedded manifest.
- `archives/minority-prophet-oneshot.zip` — formal verifier, EXP006–008
  artifacts, product reference implementation, tests, and its embedded
  manifest.
- `../../../PROVENANCE-REQUIREMENTS.md` — v2 provenance requirement stack.

## Verification performed before publication

- Handoff manifest: 15/15 entries verified.
- Final manifest: 14/14 entries verified.
- Formal verifier passed: 5,912 exhaustive worlds, 121,944 rewirings, and
  100,000 randomized trials, with zero reported violations.
- Product reference test suite: 8/8 passed.
- EXP008 reran offline. Its uploaded standalone source is byte-identical to
  the archived `final/results/exp008_shootout.py`.

## Status boundary

EXP001–002 are canonical. EXP003–008 are retained as replica or
design-validation artifacts pending porting into the repository generator,
canonical preregistration, portable runners, and independent reruns. The
paper remains a draft and is not submission-ready.

## SHA-256

| Artifact | SHA-256 |
| --- | --- |
| `archives/minority-prophet-handoff.zip` | `c2e45e89f6da03a3248fd4eba859e9405c38580f826a4f924bc7e2e222e7da7d` |
| `archives/minority-prophet-oneshot.zip` | `e227c5fbcada52136c581cc6fd88f95964d2683f2ac692363d008b2e8f27316d` |
| `../../../experiments/exp008_shootout.py` | `2f7621b26db8a0f31dbe639229335b2c3b960d957489f5a8ce3b08dfe1afef22` |
| `../../../papers/MINORITY-PROPHET-PAPER-v0.9.md` | `e662fb96a9effcfe4dc5df7509e6c211512068f80fe7c37b8b10594da9c97c96` |
| `../../../PROVENANCE-REQUIREMENTS.md` | `f605c1ad59a272d99836658a0ead547c90f23acdeddf0b666530ffb35ab31d7b` |
