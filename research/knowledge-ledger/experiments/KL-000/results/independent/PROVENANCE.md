# Independent reimplementation evidence — provenance and comparison record

Imported by RUN-20260807-2 on 2026-08-07 by copy. The originals under
`/Users/james/Development/kl000-independent-spec/` were not modified in any
way; their independence is the evidence, and this directory exists so the
repository carries its own copy of that evidence with digests binding the
copies to the originals as found.

## What was copied, and from where

| File here | Original | SHA-256 (identical for copy and original) |
|---|---|---|
| `FINDINGS.md` | `kl000-independent-spec/impl-rs/FINDINGS.md` | `af6b38376e497c22028b53da21272a28e0271013dbc783e6443c352dffe699ad` |
| `kl000-independent-result.json` | `kl000-independent-spec/impl-rs/results/kl000-independent-result.json` | `c271443fedee400b9db6d357a3d65f9f53b4591b7377f29ae90390f2ef7e2f4e` |

Digests of related originals, recorded but not copied:

| Original | SHA-256 | Note |
|---|---|---|
| `kl000-independent-spec/PROTOCOL.md` | `dea9649f…4ccf948a14` | **byte-identical** to the registered `KL-000/PROTOCOL.md` (v1.0.0) |
| `kl000-independent-spec/preregistration.json` | `5204e640…6446bcaaa5` | **byte-identical** to the registered `KL-000/preregistration.json` |
| `kl000-independent-spec/impl-rs/src/main.rs` | `e91cad52…9fb9f9a11c` | implementation entry point, for later contamination review |
| `kl000-operator-notes/OPERATOR-DISCLOSURE.md` | `d304edd1…e446419ac58c71d` | copied into the run directory (`RUN-20260807-2/evidence/`) |
| `kl000-operator-notes/NAMING-CONVERGENCE.md` | `ccb3dfe8…895252aa44d3` | copied into the run directory (`RUN-20260807-2/evidence/`) |

The byte-identity of the packaged spec to the registered spec matters: the
independent implementation was written against exactly the registered v1.0.0
documents, not a paraphrase of them.

## Strength of the independence claim

Per the operator's own disclosure, the claim is **not** "independent"
unqualified. The defensible statement, adopted here verbatim:

> Independent given a specification package that disclosed the reference
> implementation's language and module decomposition, but not its logic, its
> output field names, or any expected value.

RUN-20260807-2's grep verification found the disclosure *understates* the
leak: the packaged `preregistration.json` names five reference paths (three
`src/` modules plus both test files), not three. And one output field name in
the reimplementation (`violationsByInvariant`) matches the reference without
a visible path from the specification (see `NAMING-CONVERGENCE.md` in the
run directory); the surrounding output schema is otherwise the implementer's
own, which weakens but does not eliminate the contamination reading.

## Comparison record — what the two implementations agree on

Reference: `../kl000-confirmatory.json` (RUN-20260807-1, protocol v1.0.0).
Independent: `kl000-independent-result.json`. Derived by loading both
documents and comparing fields; re-derivable from the two files alone.

**Exhaustive phase — a reproduction.** Identical world set (independently
derived enumeration, cross-checked by count and by closed-form decomposition
in FINDINGS.md §1):

| | reference | independent |
|---|---|---|
| worlds | 176,120 | 176,120 |
| receipt-producing | 110,840 | 110,840 |
| fail-closed (single cause, ≡ I3) | 65,280 | 65,280 |
| hard-invariant violations | 0 | 0 |
| `present` | 41,820 | 41,820 |
| `absent_within_declared_scope` | 160 | 160 |
| `supported` | **19,380** | **41,820** |
| `not_established` | **49,480** | **27,040** |

The conclusion distributions disagree on **22,440 of 110,840**
receipt-producing worlds (20.2%). The independent implementation predicted
this surface before any comparison and quantified it at exactly 22,440 (its
ambiguity A3). Decomposition, verified by direct enumeration: 66 of the 163
conflict-free evidence ledgers have ≥1 supporting root with opposing ≥
supporting; 66 × 340 location ledgers = 22,440, of which support == oppose
(ties) account for 16,320 worlds and oppose > support ≥ 1 for 6,120. No
registered invariant constrains `conclusion` on this surface, which is why
both implementations passed all ten invariants while disagreeing here.
Protocol v1.1.0 repair R1 closes it.

**Randomized phase — a replication, not a reproduction.** The v1.0.0
preregistration froze the seed (20260807) but not the draw schedule or the
distribution over the declared ranges, so the two implementations sampled
*different* worlds from the same declared bounds (reference: CPython
`random.Random`, Mersenne Twister; independent: splitmix64-seeded
xoshiro256\*\* — its finding F11). What agrees is the shape, never the counts:

| | reference | independent |
|---|---|---|
| worlds | 1,000,000 | 1,000,000 |
| fail-closed rate (single cause) | 75.66% | 75.59% |
| hard-invariant violations | 0 | 0 |

The independent report additionally matches its receipt rate to the closed
form (predicted 243,686 ± 429; observed 244,091), which the reference's
243,381 also satisfies within one standard deviation.

**Not compared, by design:** digest values (each implementation's
canonicalisation was self-declared under v1.0.0 — finding F10; repaired as
v1.1.0 R4), the adversarial phases (different attack sets — finding F12), and
per-invariant checker taxonomies (the independent splits I2/I5 into a/b).

## What this does and does not establish

It establishes that an implementation written from the registered v1.0.0
documents alone, in another language with hand-written SHA-256, JSON and PRNG,
reproduced the exhaustive enumeration exactly and satisfied all ten hard
invariants over it and over a million-world replication, with a checker shown
to have power against four ablations.

It does **not** establish that the two implementations agree — they demonstrably
do not, on 20.2% of receipt-producing worlds, over a conclusion function the
specification left open until v1.1.0's R1 decided it. It does not establish
that either implementation is correct. "Verified" is not the word for this
result and is not used. The agreement that exists is agreement on the ten
invariants; the conclusion function was contested exactly where the
specification was silent.

Next gate: the independent implementation re-runs against protocol v1.1.0
(separate commission; this repository's agents do not execute it and do not
modify `impl-rs`).
