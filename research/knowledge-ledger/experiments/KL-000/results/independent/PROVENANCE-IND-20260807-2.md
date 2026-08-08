# IND-20260807-2 — provenance and comparison record

Imported by RUN-20260807-3 on 2026-08-07 by copy. Nothing under
`kl000-independent-spec/` or `kl000-v110-spec/` was modified. This extends
`PROVENANCE.md` (IND-20260807-1, imported by RUN-20260807-2); run identifiers
follow the implementer's own `IND-` sequence, with IND-20260807-1 named
retroactively by its FINDINGS-v110.md.

## What was copied

| File here | Original | SHA-256 (identical) |
|---|---|---|
| `FINDINGS-v110.md` | `impl-rs/FINDINGS-v110.md` | `c0aa3d62089331065c0a6af9cc626eac27342afbc912717e96c02263c86802e5` |
| `kl000-independent-result-v110.json` | `impl-rs/results/kl000-independent-result-v110.json` | `465032f5fa34a2b5eff5693564f5c9c87a074c3a8980869251e42788a9512c79` |

## The commission package, `kl000-v110-spec/` — digests recorded, not copied

| File | SHA-256 | Note |
|---|---|---|
| `PROTOCOL.md` | `2ce181f3…7390075c` | **byte-identical to the registered `PROTOCOL-v1.1.0.md`** — including its prediction table, which is the leak below |
| `preregistration.json` | `6a95d024…6321ba7b` | redacted variant of the registered `preregistration-v1.1.0.json` (`e9458f71…`): `expectedIdenticalToRun1` values removed in place, key still referenced elsewhere |
| `fixtures/c11-canonical-digest.json` | `b5981529…4d6aab3f` | byte-identical to the registered fixture, shipped at a flattened path; the registered path `fixtures/v1.1.0/…` does not resolve in the package (implementer finding G6, confirmed) |
| `fixtures/c01…c10` | — | the v1.0.0 controls |
| `BRIEF.md` | `6c18c7fd…a6f2f528` | commission brief |
| `RESEARCH-METHOD.md` | `2ab27ad0…27050c3b` | method document |

The original v1.0.0 package at `kl000-independent-spec/` top level is
untouched (`PROTOCOL.md` = `dea9649f…`, `preregistration.json` = `5204e640…`)
— the operator delivered v1.1.0 as a separate directory rather than
overwriting the prior package, which preserved both evidentiary states.

## The leak, traced (implementer disclosure §0 — verified, and its origin found)

The v1.1.0 package leaked every value its preregistration redaction was
written to withhold: the packaged `PROTOCOL.md`'s preregistered-prediction
table (lines 26–33) carries the exhaustive conclusion distribution, the
randomized receipt/fail-closed counts, and all four baseline totals —
including all eight values on the operator's v1.0.0 screening list,
comma-formatted. **The origin is the registration itself**: the prediction
table is scientifically necessary in a registered protocol (it is what makes
the documentation-only claim falsifiable) and fatal in a commission package,
and one file served both roles. The redaction was applied to
`preregistration.json` only.

Contamination assessment (implementer's own table, independently verified):

- **Exhaustive conclusion distribution — contaminated.** The one agreement
  line that was no longer blind. Two verified mitigations: it is derivable
  from IND-20260807-1's *published* distribution plus R1's stated rule
  (41,820 − 22,440 = 19,380; 27,040 + 22,440 = 49,480) without the leak, and
  IND-20260807-2 recomputes it from the worlds.
- **Exhaustive split, randomized counts, baseline totals — not usable for
  contamination**: derived and published in IND-20260807-1 before the package
  existed; not cross-comparable by construction (F11); ablations are the
  implementer's own with different totals.

## What conformance is now established

**Established, by two independent implementations in different languages with
no shared code:**

- **The evaluator and the conclusion function.** Identical exhaustive
  partitioning (176,120 / 110,840 / 65,280, one fail-closed cause ≡ I3) and
  — new in IND-20260807-2 — an **identical conclusion distribution**:
  present 41,820, supported 19,380, not_established 49,480,
  absent_within_declared_scope 160. The 22,440-world divergence that
  motivated v1.1.0 is closed; R1 closed it. Zero violations of all eleven
  hard invariants on both sides. Qualified by the leak note above, with both
  mitigations verified.
- **The size of the former disagreement**, measured independently twice
  (16,320 ties + 6,120 minorities), before and after the rule that settled
  it.

**Not established:**

- **I4 and I6 across implementations.** No digest has ever reproduced between
  implementations. C11's pin failed not because of a codec defect — the
  implementer's canonical bytes round-trip byte-identically through the
  protocol's own stated realisation, verified here — but because v1.1.0
  never registered the receipt *object*: 279 of C11's 703 hashed bytes are
  the values of `schema`, `reason` and `limits`, stated nowhere (finding G2).
  Until a digest reproduces, deterministic replay and digest integrity are
  per-implementation properties only. This is what RUN-20260807-3's R5.1
  exists to repair.
- **The randomized phase across implementations** — still a replication on
  different streams (F11 open).
- **That the conclusion function is enforced.** G4, verified here: an
  evaluator with the inverted (existential) presence reading changes 22,440
  conclusions, violates zero invariants, and is caught only by fixture C11.
  The rule is registered prose plus one fixture, not an invariant.

The implementer's own closing description of its independence, adopted:

> Independent given a specification package that disclosed the reference
> implementation's language, its complete file inventory, and — in v1.1.0 —
> every expected count the redaction was written to withhold. No invariant
> logic and no receipt field name was disclosed, which is why C11's digest
> could not be reproduced and was not tuned toward.

Next gate: IND-20260807-3, the re-run against v1.2.0 attempting C11 again.
Separate commission; the packaging must this time screen `PROTOCOL.md` as
well as the preregistration (the prediction table must not ship), and the
registered fixture paths must resolve.
