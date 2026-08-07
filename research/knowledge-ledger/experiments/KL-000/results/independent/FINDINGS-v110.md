# KL-000 v1.1.0 — independent re-run: results and findings

**Run identifier: IND-20260807-2.** Predecessor: **IND-20260807-1**, this same
Rust implementation against protocol v1.0.0 (`FINDINGS.md`), which was named
retroactively — it carried no identifier when produced and was cited only as
"imported by RUN-20260807-2". `IND-` is a separate sequence from the reference
repository's `RUN-` numbering by design: a `RUN-` number would imply that
repository's agents executed this work.

The implementation was **updated in place**, not rewritten. The reference
implementation was not located, opened, or read in either run.

Overall status: **`passed-except-c11-digest`** — 0 hard-invariant violations by
B5 across all four phases, all eleven controls matching every registered *value*,
all four preregistered baselines caught, and **C11's pinned `contentDigest` not
reproduced**. That last item is finding G2 and is not a bug in this
implementation.

---

## 0. Disclosure first: the v1.1.0 package leaks every value it withholds

`preregistration.json` redacts `expectedIdenticalToRun1` and says why, in place.
That redaction is defeated by `PROTOCOL.md` in the same package. Its
"Preregistered prediction" table (lines 26–33) states the exhaustive conclusion
distribution, the randomized receipt and fail-closed counts, and all four
baseline violation counts.

`OPERATOR-DISCLOSURE.md` records the eight values the operator screened the
v1.0.0 package against:

```
110840  243381  65280  756619  634440  189720  26880  26208
```

**All eight are present in the v1.1.0 package.** Seven are in PROTOCOL.md; a
grep reproduces this in one line. This is the same class of error as the v1.0.0
`artifacts` leak, in the version written to correct it, and it is strictly
larger: v1.0.0 leaked structure, v1.1.0 leaks the answers.

**I read PROTOCOL.md before implementing — it is the specification — so I saw
them.** What that could and could not contaminate:

| leaked value | exposure |
|---|---|
| 110,840 / 65,280 exhaustive split | none. Derived from the declared bounds and reported in IND-20260807-1 before this package existed. |
| exhaustive conclusions 160 / 49,480 / 41,820 / 19,380 | **real.** This line is no longer blind. It is however derivable from my own v1.0.0 output plus R1's stated rule, without the leak: I reported 160 / 27,040 / 41,820 / 41,820 and measured A3's surface at 22,440; R1 moves exactly those 22,440 from `supported` to `not_established`, giving 19,380 and 49,480. My run recomputes both columns from the worlds (§3) rather than asserting either. |
| randomized 243,381 / 756,619 | none. Cannot match by construction (F11). Mine are 244,091 / 755,909, unchanged from v1.0.0. |
| baselines 634,440 / 26,880 / 26,208 / 189,720 | none. My ablations are my own; mine are 1,218,240 / 124,280 / 26,880 / 687,480. The single coincidence (26,880) is my B3 against the reference's B2, and I did not adjust anything. |

*Recommended repair:* screen `PROTOCOL.md`, not only `preregistration.json`. The
v1.0.0 disclosure's own lesson — that a check which passes can still be scoped
to the wrong file — recurred here on the next file along.

---

## 1. Counts per phase

### Fixture (C01–C11)

**11 / 11 match on every registered value field**, first execution, no
tolerances. C11's `conclusion` is `not_established`, so **R1's tie rule is
satisfied**, and its `margin` of 0, `distinctRoots` 2 and
`repeatedRecordsCollapsed` 1 all match.

**C11's `contentDigest` does not match.** Pinned
`sha256:84e63c…33eafe`; computed `sha256:0d178b…89c68`. See §4, finding G2.

### Exhaustive-small

| | IND-20260807-2 | IND-20260807-1 | moved |
|---|---|---|---|
| worlds enumerated | 176,120 | 176,120 | — |
| receipt-producing | **110,840** | 110,840 | — |
| fail-closed | **65,280** | 65,280 | — |
| fail-closed causes | `root_on_both_sides` ×65,280, one cause | same | — |
| hard violations | **0** | 0 | — |
| `absent_within_declared_scope` | **160** | 160 | — |
| `present` | **41,820** | 41,820 | — |
| `not_established` | **49,480** | 27,040 | **+22,440** |
| `supported` | **19,380** | 41,820 | **−22,440** |

Wall clock 12.1 s, 14,580 worlds/s.

### Randomized

Seed 20260807, 1,000,000 worlds, unchanged bounds and unchanged draw schedule.

| | IND-20260807-2 | IND-20260807-1 | moved |
|---|---|---|---|
| receipt-producing | **244,091** | 244,091 | — |
| fail-closed | **755,909** | 755,909 | — |
| fail-closed causes | `root_on_both_sides` ×755,909, one cause | same | — |
| hard violations | **0** | 0 | — |
| `absent_within_declared_scope` | **1,070** | 1,070 | — |
| `present` | **82,077** | 82,077 | — |
| `not_established` | **119,641** | 79,032 | **+40,609** |
| `supported` | **41,303** | 81,912 | **−40,609** |

Seed reproduces a bit-identical stream (`fnv1a64:4dee7326f948b0fe`); generator
inside declared bounds; no unexpected fail-closed cause. 36.0 s, 27,748
worlds/s. **Still not cross-comparable** — F11 is open and v1.1.0 says so.

### Adversarial

**12 / 12.** A01–A10 carried from IND-20260807-1; A06 and A07 are reclassified
from defect probes to permanent regression tests, since R2 and I11 now *require*
the refusals they exercise. Two new: **A11** pins R1 at a tie, a strict minority
and a strict majority; **A12** pins R4's escaping with a quote, a backslash, an
em dash and an accented letter in one proposition.

### Baselines, full 176,120-world set

| baseline | violations | by invariant |
|---|---|---|
| B1 head-count | 1,218,240 | I1 828,240 · I10 297,840 · I3 65,280 · I2a 13,440 · I2b 13,440 |
| B2 source-count | 124,280 | I8 110,840 · I2b 13,440 · **I2a 0** |
| B3 evidence-without-coverage | 26,880 | I2a 13,440 · I2b 13,440 |
| B4 search-without-collapse | 687,480 | I1 520,200 · I10 167,280 |

All non-zero: the checker has power. B1 and B4 rose (816,000→828,240 and
514,080→520,200) purely because R1 changes some ablated conclusions, so I1's
"conclusion unchanged under duplication" clause fires on more worlds. B2's
**I2a count is still 0** — open finding F1, unrepaired and now formally
acknowledged in v1.1.0's own baseline note.

---

## 2. Did the repairs move any number of mine?

**R2 and R3 moved nothing, exactly as v1.1.0 predicts.** Both required behaviour
IND-20260807-1 already had, unprompted: the empty-ledger refusal
(`empty_search_ledger`) and the duplicate-location-id refusal
(`duplicate_location_id`). I changed their *status* in the code, not their
effect. I11 is now a tracked invariant: exercised on 110,840 exhaustive and
244,091 randomized worlds, 0 violations, and its refusal path is exercised only
adversarially — as v1.1.0 says it would be.

**R4 moved nothing.** My v1.0.0 codec emitted every C0 control as `\u00XX`;
v1.1.0 requires `\b \t \n \f \r` for five of them. No receipt this evaluator
emits contains a control character, so no digest in either run changes. I
implemented the stated rule anyway.

**R1 moved 22,440 exhaustive receipts and 40,609 randomized ones**, which is the
one place v1.1.0 predicted movement for me and not for the reference. My run
recomputes both distributions over the same worlds:

- 22,440 receipts change conclusion: **16,320 ties** and **6,120 strict
  minorities**.

PROTOCOL.md states 16,320 + 6,120 independently. Mine were computed from the
enumeration, not read off. This is the sharpest agreement in either run, because
it is agreement about the *size of a disagreement* — measured twice, from two
implementations, before and after the rule that settled it.

I accept R1. It is the owner's call, it is stated, and it is now conformance. I
still think the existential reading was defensible, and I note v1.1.0 preserves
that view in the record rather than overwriting it, which is the right handling.

---

## 3. Which of my ambiguities the repairs closed

| | ambiguity | status under v1.1.0 | worlds it governs |
|---|---|---|---|
| A1 | does absence need supporting evidence? | **closed** — `conclusionFunction.absence` gates on coverage alone | 4 |
| A2 | does presence need complete coverage? | **closed** — `conclusionFunction.presence` states the rule with no coverage term | 19,152 |
| A3 | ties and minorities on presence claims | **closed** — R1, owner decision | 22,440 |
| A4 | is `margin` signed or absolute? | **listed open (F5) — but closed by accident.** See G1 | 38,760 |

Closed by text, not by test: **no invariant enforces any of these.** See G4.

Of my fifteen v1.0.0 findings, v1.1.0 repairs F8, F9, F10 (partly), lists F1–F5,
F11–F14 as open, and does not mention **F6, F7 or F15**. F6 and F7 were in fact
closed by `conclusionFunction` — see G5. F15 dropped out of the record entirely.

---

## 4. C11: the pinned digest does not reproduce, and my codec is not why

This is the repair that mattered most, and it half-worked. Written down before
any adjustment, as instructed; nothing was tuned.

**What matches.** Every value field of C11. R1's tie rule, the collapse
arithmetic, the search arithmetic, `margin` 0, `conversionsToReverse` 1.

**What does not.** The digest.

```
pinned    sha256:84e63c21271a19c3bfbb1d42c5ce61e60288456a48c33829a66ae916bc33eafe
computed  sha256:0d178b7f8a8057c6fec0aa9d8f013ad362df43074e759afb6f6e1218ab389c68
```

**Why it is not my codec.** Three independent checks:

1. Seven rule-by-rule vectors (sorted keys, no whitespace, `\"`/`\\`, the five
   two-character control escapes, other C0 as lowercase `\u00XX`, raw UTF-8 at
   and above U+0020, arrays unreordered, plain integers) all conform, and are
   recorded in `canonicalFormConformance` in the result.
2. **The unsigned canonical form I produce for C11 is byte-identical to the
   protocol's own stated realisation** —
   `json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False)`
   — round-tripped externally. My codec *is* `canonicalForm`.
3. A12 confirms the escaping end-to-end on a proposition carrying `"`, `\`,
   U+2014 and U+00E9.

**Why it is.** The receipt objects differ.

| | |
|---|---|
| my unsigned canonical form | **463 bytes** |
| protocol's stated unsigned form | **703 bytes** |
| my receipt's members | `receiptVersion, transactionId, claim, conclusion, search, evidence, contentDigest` |
| R4's digest scope names | `schema, transactionId, claim, search, evidence, conclusion, reason, limits` |

Of the members R4 declares covered, the package states the **values** of five:
`transactionId`, `claim`, `search`, `evidence`, `conclusion` — all readable off
C11 itself. Their canonical length is **424 bytes**. The remaining **279 bytes,
40% of what C11 hashes, are the values of `schema`, `reason` and `limits`, which
no document in the package defines.**

### G2 — R4 defines the canonical form but not the receipt

The digest is a function of two things: a codec and an object. R4 pins the
codec and the removal rule, and pins neither the receipt's member list nor the
values of three members it explicitly names as covered. **No conforming
implementation can compute C11's digest from the v1.1.0 specification.**

So C11 is not, as registered, a cross-implementation test of I4 and I6. It is a
test of whether an implementation happens to emit the reference's receipt
schema. Passing it requires information the package withholds; failing it says
nothing about the canonicalisation. F10 is about 60% repaired — the 60% that is
bytes-per-value, not the 40% that is which-values.

*Recommended repair:* register the receipt schema. Give C11's `expected` block
the full unsigned canonical string, or at minimum the values of `schema`,
`reason` and `limits`. One line in the fixture makes I4 and I6 genuinely
cross-testable; without it they remain what IND-20260807-1 called them,
self-referential.

I have not adopted a guessed receipt schema and will not: reverse-engineering
279 unknown bytes from a 256-bit target is tuning toward a withheld answer, and
a match obtained that way would measure nothing. If the schema is registered,
this is a one-line change and I will re-run.

---

## 5. Findings new in v1.1.0

### G1 — R4 rule 6 closes F5 by the back door, and v1.1.0 says it deliberately did not

`canonicalForm.numbers`: *"receipts contain only non-negative integers … a
receipt containing a float or null has no defined canonical form under this
protocol."*

`margin` is the only receipt field that can be negative, and its sign is
**listed as open** in v1.1.0's own `openFindings` (F5). PROTOCOL.md goes further
and says C11's `margin` was *made* 0 so the fixture "does not silently resolve
the still-open margin-sign ambiguity". Rule 6 resolves it anyway, three sections
earlier, by asserting the property that only the absolute reading has.

The two statements cannot both hold. Under the signed reading — mine, registered
in IND-20260807-1 and still open per v1.1.0 — the count of receipts the protocol
leaves without a canonical form is:

| phase | receipts | with a negative integer | share |
|---|---|---|---|
| exhaustive | 110,840 | **38,760** | 35.0% |
| randomized | 244,091 | **82,830** | 33.9% |

For those receipts **I4 and I6 are undefined**, because the invariants are stated
over a canonical form the protocol declines to give them. Zero under the absolute
reading.

I kept `signed` and counted, rather than switching to make the contradiction
disappear. Either v1.1.0 decided F5 in favour of absolute margin — in which case
it is a fifth repair and should be listed, with C11's sign-agnosticism recorded
as moot — or rule 6 should read "integers" and drop "non-negative". As written
the specification contradicts itself, and the contradiction is load-bearing for a
third of all receipts.

### G4 — the repairs fixed the text; the test surface is unchanged

PROTOCOL.md v1.1.0 diagnoses v1.0.0 precisely: *"No invariant constrains
`conclusion`, so the divergence was invisible to the entire v1.0.0 test
surface."* That sentence is still true of v1.1.0.

Measured, by running the same checker over an ablation that inverts R1 — which
is exactly my v1.0.0 reading:

| | |
|---|---|
| worlds whose conclusion the ablation changes | **22,440** |
| invariant violations detected, I1–I11 | **0** |
| registered fixtures that catch it | **C11, and only C11** |

An evaluator that gets the presence rule backwards passes all eleven hard
invariants over the complete 176,120-world enumeration and one million randomized
worlds. Its entire detection surface is one world in one fixture. `conclusionFunction`
is now registered prose with no invariant behind it, so the structural defect
that produced the 22,440-world divergence is intact; only the specific
disagreement was resolved.

R3 shows the right instinct — R3 made a rule into invariant I11 precisely so it
would be *checked*, and argues carefully for a separate invariant over an
extension of I8. R1 deserved the same treatment and did not get it.

*Recommended repair:* an I12 — `conclusion` equals `conclusionFunction` applied
to the world — which subsumes I2's and I5's conclusion clauses and would have
caught this divergence in v1.0.0 without any fixture.

### G5 — `conclusionFunction` is a fifth repair, unlisted

v1.1.0 says its repair list "is exactly R1–R4". But `conclusionFunction` closes
two further ambiguities that R1–R4 do not mention:

- `conclusionFunction.absence` gates absence on coverage alone, closing **A1 /
  finding F7** (4 exhaustive worlds);
- `conclusionFunction.presence` states the presence rule with no coverage term,
  closing **A2 / finding F6** (19,152 exhaustive worlds).

For me the numeric change is zero, because I already read both that way. But
v1.1.0's central claim is that only documented behaviour changed and that R1 is
the only rule whose reading was contested. A third implementation that had read
A2 the other way — a reading nothing in v1.0.0 excluded — would move **19,152
worlds** on adopting v1.1.0, attributable to no listed repair. The claim
"documentation-only" is being tested against one other implementation, and it is
weaker than it looks against an arbitrary one.

### G6 — smaller

- **C11's path.** PROTOCOL.md and `preregistration.json` both give
  `fixtures/v1.1.0/c11-canonical-digest.json`; the package ships it at
  `fixtures/c11-canonical-digest.json`. My loader tries both. Harmless, but it is
  a registered path that does not resolve.
- **I9 is still exercised zero times** by the fixture, exhaustive and randomized
  phases — unchanged from IND-20260807-1, in both runs, for all 1,176,120
  enumerated worlds. It is not in v1.1.0's `openFindings`, so it is now neither
  repaired nor recorded. Same for F15.
- **`uncertainty.randomizedPhase`** says "eight of the invariants are exercised
  on 243,381 receipt-producing worlds" without saying which eight. By my count
  ten are exercised on receipt-producing worlds, I3 on all worlds, and I9 on none.
- **C06's note (F13) is still wrong** and still shipped, in a fixture set
  described as "byte-identical to its v1.0.0 registration". Preserving the bytes
  is right; the note is a known error being carried forward, and nothing in the
  package marks the fixture itself as carrying a correction.

---

## 6. What I think v1.1.0 gets right

Worth saying, since the rest of this document is defects.

- **R3's reasoning is the best thing in the document.** Registering I11 as a new
  invariant rather than extending I8, with the argument stated — different
  observable, different code path, and cross-version comparability of I8's counts
  preserved — is more careful than the repair needed to be.
- **R1 is labelled an owner decision, and the rejected reading is preserved with
  its rationale.** That is the correct handling of a judgement call, and it is
  rarer than it should be.
- **The preregistered prediction table with "if any number moves, the run halts
  and the deviation is reported as a finding"** makes the documentation-only
  claim falsifiable rather than rhetorical. My numbers are the evidence for that
  claim on my side: R2, R3 and R4 moved nothing of mine either, and I could not
  have arranged that after the fact, because IND-20260807-1's numbers were
  published first.
- **`conclusionFunction` exists at all.** Putting the conclusion rule inside the
  registration is the single most important change in v1.1.0, and G4 is a
  complaint about its enforcement, not its presence.

---

## 7. What this run establishes

That this implementation, updated in place from IND-20260807-1 and still never
having seen the reference, conforms to protocol v1.1.0 across 176,120 enumerated
and 1,000,000 seeded worlds with **zero violations of all eleven hard
invariants**, matches **every registered value** of all eleven controls, and is
caught by none of four ablations that the same checker catches.

It does **not** establish that C11's digest is wrong — only that it is not
computable from the specification. It does not establish that the two
implementations agree on anything not in this package; the randomized phase
remains a replication. And per G4 it does not establish that the conclusion
function is right, only that mine now matches the one written down — which is a
statement about a document, not about the world.

The honest description, extending the operator's own phrasing:

> Independent given a specification package that disclosed the reference
> implementation's language, its complete file inventory, and — in v1.1.0 —
> every expected count the redaction was written to withhold. No invariant
> logic and no receipt field name was disclosed, which is why C11's digest
> could not be reproduced and was not tuned toward.
