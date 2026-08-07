# DRAFT RUN REPORT v1 — RUN-20260807-2

KL-000 specification repair and re-run. Protocol v1.1.0 registered and passed
with every number identical to RUN-20260807-1. Draft only; nothing pushed,
nothing promoted.

## What happened, in one paragraph

The independent Rust reimplementation of KL-000, commissioned after
RUN-20260807-1, completed: it reproduced the exhaustive enumeration exactly
(176,120 / 110,840 / 65,280 / 0) and passed all ten invariants, while
disagreeing with the reference on the `conclusion` of 22,440 of 110,840
receipt-producing worlds — a divergence it predicted and quantified before any
comparison, and one no invariant constrained. This run imported that evidence
with provenance, registered protocol v1.1.0 carrying four specification
repairs (all verified beforehand to describe behaviour both implementations
already have), re-ran KL-000 in full against v1.1.0, and confirmed the
registered prediction: **no number moved**. The identical numbers are the
evidence that the repairs were documentation, not behaviour change.

## The four repairs, and who decided them

| | Repair | Origin | Decided by | Verified existing behaviour |
|---|---|---|---|---|
| R1 | Presence-claim tie rule: `supported` iff supporting roots strictly exceed opposing; ties (and minorities) are `not_established` | ambiguity A3, the 22,440-world divergence | **owner — a decision, not a derivation; could defensibly have gone the other way** (the implementer's contrary existential reading is preserved in FINDINGS.md) | `transaction.py:69`, probed |
| R2 | `complete` requires `declared > 0`; empty declared scope refuses | finding F8 (vacuous absence for a zero-location ledger) | owner, adopting the unprompted repair both implementations made | both refuse; probed |
| R3 | Location-id uniqueness, registered as **new invariant I11** (not an I8 extension: I11 is an admissibility rule, I8 is receipt arithmetic) | finding F9 (duplicate ids inflate `declared` — the search-ledger mirror of the I1 copy attack) | owner, adopting the unprompted repair both implementations made | both refuse; probed |
| R4 | Canonical JSON and digest scope defined; fixture C11 pins an expected `contentDigest` | finding F10 (I4/I6 constrained an implementation against itself) | owner, adopting the reference's canonicalisation | digest recomputed; C11 pinned before registration |

C11 is the first KL-000 value a second implementation can be *wrong about*
rather than merely different from. It was deliberately built sign-agnostic in
`margin` so it does not smuggle in a resolution of the still-open margin-sign
ambiguity (F5).

## The re-run: registered prediction met exactly

`preregistration-v1.1.0.json` registered the RUN-20260807-1 numbers as an
exact-equality prediction (`expectedIdenticalToRun1`) with a halt-and-report
condition on any deviation. Observed, label `confirmatory-v1.1.0`, result
`passed`, zero invalidation reasons:

```
fixtures     11/11 (C01-C10 unchanged; C11 digest matches its pin)
exhaustive   176,120 worlds   110,840 receipts   65,280 fail-closed   0 violations
             conclusions 160 / 49,480 / 41,820 / 19,380
randomized   1,000,000 worlds  243,381 receipts  756,619 fail-closed  0 violations
baselines    B1 634,440   B2 26,880   B3 26,208   B4 189,720   all caught
fail-closed  one cause per phase (root on both sides ≡ I3)
```

Every value equals RUN-20260807-1's; the comparison log is
`logs/v110-vs-run1-comparison.txt` and the check is reproducible from
`REPRODUCE-v1.1.0.md`. Evaluator hash unchanged
(`15dfd500…3a3e21f`); both registration chains verify
(`PROTOCOL-COMMIT.txt` = `c977347…`, `PROTOCOL-COMMIT-v1.1.0.txt` =
`1a8256f…`); 74 repo tests and 68 KL-000 tests pass (14 new, pinning R1–R4).

## What the reproduction did and did not establish — the record, stated carefully

**Established.** An implementation written from the registered v1.0.0
documents alone — different language, hand-written SHA-256/JSON/PRNG —
independently derived the same 176,120-world enumeration, agreed exactly on
receipt/fail-closed partitioning with a single fail-closed cause, and
satisfied all ten hard invariants over it, with a checker demonstrated
non-vacuous against four ablations. The exhaustive phase is a **reproduction**.

**Not established.** Agreement of the two implementations: they disagree on
20.2% of receipt-producing conclusions (`supported` vs `not_established`),
over a conclusion function the v1.0.0 specification did not constrain —
contested until R1 decided it. The randomized phase is a **replication, not a
reproduction**: the seed froze no cross-implementation stream (F11), so its
agreement is "0 violations at an equivalent fail-closed rate", never
count-for-count. **"Verified" is not the word for any of this and is used
nowhere in the record.** The independent implementation has not run against
v1.1.0; whether R1–R4 close the divergence is exactly what the next gate
tests.

**Independence, at its true strength** (operator's own disclosure, verified
here by grep and found to *understate* the leak): the specification package
disclosed the reference's language and module decomposition — five reference
paths, not the three the disclosure lists, including both test filenames —
but not its logic, output field names, or any expected value. One
reimplementation output field (`violationsByInvariant`) matches the reference
with no visible path from the specification; the surrounding schema is
otherwise the implementer's own, which weakens the contamination reading
without eliminating it. Recorded, not adjudicated: `atime` is disabled, so it
cannot be settled by inspection. Both operator notes are preserved in
`RUN-20260807-2/evidence/` and the qualified claim is restated in
`results/independent/PROVENANCE.md`.

## Findings opened by this run

- **SPEC-101 (central).** An invariant suite can pass in two implementations
  that disagree on the primary output: no v1.0.0 invariant constrained
  `conclusion`, so a 22,440-world divergence was invisible to fixtures,
  enumeration, randomization, adversarial attacks, and baselines in both
  implementations simultaneously. Repaired for the tie/minority surface by
  R1 + C11; the general lesson (every field a downstream consumer reads needs
  an invariant or a pinned fixture) is methodology note M7.
- **NAM-101 (minor).** The registration's baseline ids
  (`B3-evidence-ledger-without-coverage`) and the runner's report keys
  (`B3-evidence-without-coverage`) are different spellings of the same
  objects, in v1.0.0 and inherited by v1.1.0's prediction table. Found when
  this run's comparison script crashed on the mismatch; mapped explicitly in
  the committed comparison. One vocabulary should win in v1.2.0.
- **Prompt capture is agent-transcription again** (PROV-004 recurrence): no
  operator-side prompt artifact existed for this run; the digest in
  `run-manifest.json` is marked unverified accordingly.

Deliberately **not** repaired (owner's list was exactly R1–R4): F1/F2
(receipt-internal I2/I5, including the measured fact that registered B2 does
not fail literal I2), F3 (B2≡B3), F4/F5 (`conversionsToReverse` at the empty
ledger; margin sign — 38,760 worlds), F11–F14. All carried in the backlog as
v1.2.0 candidates with the independent implementer's recommended repairs.

## Commits of this run

| SHA | What |
|---|---|
| `544ea1e` | run open: orientation, prompt capture, verification of claims |
| `226a9f2` | evidence import by copy + provenance and comparison record |
| `1a8256f` | **registration commit** — protocol v1.1.0, preregistration, fixture C11 |
| `cc18ce6` | execution support: `--preregistration`, digest-pinned fixtures, I11/R2 admissibility, 14 tests, sidecar |
| `ddf4025` | **result commit** — v1.1.0 confirmatory, passed, identical numbers |
| `a477a07` | STATUS: next gate = independent re-run against v1.1.0 |
| *(packet)* | this closing packet |

Registration precedes implementation support and result; both sidecar chains
verify in both directions.

## What this licenses, and does not

KL-000 remains `adversarial-passed` — now under both protocol versions — and
is **not** `verified-independent`. No promotion is performed: EXPERIMENT-
REGISTRY.json, CANONICAL-RECORDS.md, PUBLIC-CLAIMS.md, and the paper are
untouched. KL-011 remains blocked on the same artifact as before, now
sharpened: the independent implementation re-running against v1.1.0, a
separate commission that this repository's agents must not execute and whose
target (v1.1.0) must not move while it is out. No First Transmission and no
Candidate First Transmission is claimed or claimable.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
