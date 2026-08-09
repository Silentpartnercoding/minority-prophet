# FINDING-BL051 — LIN-000 v0.2, independent reimplementation

Commissioned by RUN-20260808-3 (`BRIEF.md`). Registration under test:
`REGISTRATION-v0.2.md`, committed at `7c8233c` before the v0.2 reference existed.

**The question the commission asks:**

> Does your pre-declared reading hit both digests, with no sweep?

**Answer: yes. Both digests, and all 150 prefix digests, on the first run, from a
reading frozen before any code was written.**

| | pre-declared result | pinned | |
|---|---|---|---|
| exhaustive total | `a71c64eb…3be711` | `a71c64eb…3be711` | **hit** |
| randomized total | `e69fc115…2a2a3e` | `e69fc115…2a2a3e` | **hit** |
| exhaustive prefixes | 50 of 50 | 50 | **all hit** |
| randomized prefixes | 100 of 100 | 100 | **all hit** |

No sweep was run before the comparison. No reading was amended after it. The
pre-declaration is `DECISIONS.md`, SHA-256
`1e2be675e04beac82c4cbbe5442e35a30c6ba032174e28eb27352b69396eb83b`, unchanged
from the moment it was frozen (verify against `RUN-MANIFEST.json`, written after
the run).

The remainder of this report is the part that carries information: what was still
undetermined, what the tests did, and what I think is wrong with the registration.
**The most consequential result here is not the hit — it is §5.1**, where a term
the registration never defines decides whether a theorem it registers as
"MUST be 0" is true or has 47,224 counterexamples.

---

## 0. Compliance

- **The reference implementations were not read.** Nothing under
  `research/knowledge-ledger/lineage/` was opened, listed, globbed, or searched.
  No file outside this package was read at any point.
- **No Python.** Two implementations, both non-Python:
  - **Rust** (`impl-rust/lin000.rs`), primary. No external crates. **SHA-256
    written by hand from FIPS 180-4** — the implementation shares no hashing code
    with any other program on this machine.
  - **JavaScript on Node.js** (`impl-node/lin000.mjs`), independent cross-check,
    using `node:crypto` (OpenSSL). A completely separate SHA-256 code path.
- `MANIFEST.sha256` verified before starting: all four shipped files OK.
- SHA-256 self-tested against four FIPS 180-4 vectors in both implementations, and
  `block(0)` verified against the system `shasum` binary:
  `SHA-256(00000000013527c8 || 0000000000000000)` =
  `5dcac6d3a27f75c0f597656448efe5c86cab22d06638d1c1fec7fcc1dd6fabcd`, which is
  what my generator produces.
- The two implementations were required to agree with **each other** on every
  reported field before `PINNED-DIGESTS.json` was opened for comparison. They did.

---

## 1. Declared bounds, derived rather than adopted

The brief asks that `50,362` be derived, not taken.

Position `i` admits `(i+1)` parents (`null` plus the `i` earlier claims) and 2
sides, independently across positions, so `count(k) = k! · 2^k`:

| k | 1 | 2 | 3 | 4 | 5 | 6 | total |
|---|---|---|---|---|---|---|---|
| count | 2 | 8 | 48 | 384 | 3,840 | 46,080 | **50,362** |

**Agrees with the registration.** The enumerator emitted exactly 50,362 worlds.
No disagreement to report.

The randomized phase consumed **2,759,273 words** across 100,000 worlds
(~27.6 words/world), and its `k` histogram is flat across 1..20 (min 4,827,
max 5,062) — consistent with `k = 1 + uniform_below(20)`.

---

## 2. Both phases, in full

```
exhaustive   worlds 50,362   digest a71c64ebd472db09ff7813a1a470d002c014a6a4d0cbd6b515aaad61ef3be711
             regenerated in-run: identical      prefixes 50/50 match, no divergence
randomized   worlds 100,000  digest e69fc115e77f8020700a681ceab4459972873bcccecb679b597c0641b32a2a3e
             regenerated in-run: identical      prefixes 100/100 match, no divergence
```

There is no divergent prefix block to report, in either phase. The prefix digests
were opened only after both totals had already been compared, and were used only
to confirm that agreement held throughout rather than coincidentally at the end.
They were never used to steer a reading; the frozen reading was never edited.

Every invalidation condition in §Invalidation was checked and none fired:
exhaustive count = 50,362 ✓; no expected-nonzero count observed zero ✓; no float
in any sampler ✓; both phases regenerated identically within the run ✓.

**Frozen concrete prediction, checked.** `DECISIONS.md` §R14 committed the first
ten worlds of the exhaustive stream before implementation. Emitted:
`-|0`, `-|1`, `-|0;-|0`, `-|0;-|1`, `-|0;0|0`, `-|0;0|1`, `-|1;-|0`, `-|1;-|1`,
`-|1;0|0`, `-|1;0|1` — identical to the prediction.

### 2.1 How much of the agreement is evidence

The brief's disclosure is load-bearing and I take it at face value: the exhaustive
order was written after reading the v0.1 implementer's decision log and adopts
their reading, so my agreeing with it is weaker evidence than a blind match.

I would put it slightly differently, in v0.2's favour. v0.2 does not ask a reader
to *infer* the enumeration order — it **states** it, in three numbered clauses.
What my exhaustive hit measures is therefore not "is this the natural order" but
"is the stated order stated unambiguously". That is a smaller claim than the
disclosure worries about, and it is the claim v0.2 actually needs. The disclosure
would bite if v0.2 had left the order implicit; it did not.

The randomized hit carries no such caveat. Its generator is new, its digest
matches nothing from v0.1, and reproducing it required agreeing on the seed
encoding, the counter encoding, word extraction, the rejection rule, the
degenerate `uniform_below(1)` case, per-claim draw order, the claim-0 boundary,
and stream continuity across worlds — every one of them independently, with no
feedback. **That is the cross-language result the programme was after.**

---

## 3. Ambiguities I still had to resolve

v0.2 claims to have removed the ambiguity. Measured honestly, here is the tally.

**Choices that affect the two digests: 0 were undetermined.** Every one was
decided by the registration text. Four required care rather than mere reading:

| | choice | what decided it |
|---|---|---|
| R1 | seed as `uint64_be`, **not** ASCII `"20260808"` | the word "big-endian" — a byte string has no endianness. Note the trap: the decimal seed is *exactly* 8 bytes, so "encoded as 8 bytes" alone does not separate them |
| R5 | one continuous stream across all 100,000 worlds, no per-world reseed | "Draws are consumed strictly in order, starting at `w(0)`" |
| R15 | no trailing `;`, single `\n`, `-` for root, ASCII | §Canonical stream form, read literally |
| R17 | prefix digest = digest of a genuine byte prefix at each completed 1,000 worlds | §Prefix digests; corroborated by the published entry **counts** (50 and 100) before running — counts only, never values |

The rejected alternatives are listed in `DECISIONS.md`; §4 below measures what
each would have cost.

**Choices that affect the theorem tests: 4 were undetermined, and I had to invent
all four.**

1. **What a "rewiring" is** (§R23). The registration asserts T1 over rewirings
   without saying what may move, what "root-preserving" means, or over which
   population. See §5.1 — this is not a cosmetic gap.
2. **What the shallow-`S_a` ablation is** (§R24). Named, not constructed.
3. **What the claim-count ablation is** (§R24). Named, not constructed.
4. **The population for L1-negative** (§R22). "MUST exist" over which worlds?

There is a clean pattern in that tally, and it is the finding for this item:

> **v0.2 closed the stream-reproduction gap completely and did not touch the
> theorem-test gap at all.** Every ambiguity I had left was in a section that does
> not feed a digest — which is exactly why the digests could still match while
> the tests remained under-determined.

D1, D2 and D3 were the right three defects and they are fixed. The next
registration's defect list should start at §Tests that can fail.

---

## 4. How load-bearing was each decision? (post-hoc sensitivity)

Run **after** the pre-declared hit, purely to measure whether v0.2's precision was
necessary or merely tidy. Each variant changes one decision away from the frozen
reading — 19 perturbed readings in all, 18 of them single-decision plus one
deliberate combination. Full output: `results/variants.json`.

**Randomized phase — 13 readings tested, 13 distinct digests, exactly 1 hit:**

| reading | digest | |
|---|---|---|
| frozen reading | `e69fc115…` | **hit** |
| seed as ASCII `"20260808"` | `553830fc…` | miss |
| seed as `uint64_le` | `28ae976c…` | miss |
| counter as `uint32_be` | `1edbb830…` | miss |
| words read little-endian | `dd18e6a3…` | miss |
| `uniform_below(1)` short-circuits | `d2175c5a…` | miss |
| float sampler `floor(w/2^32·n)` (forbidden by §Invalidation) | `7665b34c…` | miss |
| claim 0 consumes a root-decision draw | `82ab90ee…` | miss |
| side drawn before parent | `6e254cb6…` | miss |
| generator reseeds per world | `a915aade…` | miss |
| trailing `;` | `e3731171…` | miss |
| root rendered `null` | `ddd3b084…` | miss |
| claims joined with `,` | `926558bc…` | miss |

**Exhaustive phase — 8 readings tested, 8 distinct digests, exactly 1 hit:**
side-major within a position, `null` ordered last, position 0 fastest, descending
`k`, side-major + null-last, trailing `;`, root as `null` — all miss.

Three things follow.

- **Every clause v0.2 added is load-bearing.** D2's degenerate case is not a
  hypothetical: `uniform_below(1)` was called **66,427 times**, and the
  short-circuit reading misses. The claim-0 boundary — v0.1's coin flip — misses
  if decided the other way. Had v0.2 left these open, the sweep would again have
  been multiplicative across at least a dozen binary and ordering choices.
- **The float prohibition is enforceable after all.** §Invalidation forbids a
  float sampler, which reads like a code-inspection rule a verifier cannot check.
  It is in fact observable: `floor(w/2^32·n)` diverges (`7665b34c…`). Worth
  restating in the registration as a *consequence* rather than an honour system.
- **One clause is not load-bearing, and that is a problem — see §5.2.**

---

## 5. Did Theorem 1 or Lemma 1 fail anywhere?

**Under my pre-declared reading: no. Under an alternative admissible reading of a
term the registration leaves undefined: yes, 47,224 times.**

All counts below are exhaustive, not sampled.

| test | population | result |
|---|---|---|
| L1-positive | 5,912 side-consistent exhaustive worlds | **0 violations** |
| L1-positive | 54,747 side-consistent randomized worlds | **0 violations** |
| L1-negative | 44,450 side-inconsistent exhaustive worlds | **44,450 hits** |
| L1-negative | 45,253 side-inconsistent randomized worlds | **45,253 hits** |
| T1-positive | 57,240 root-preserving side-consistent rewirings | **0 violations** |
| T1-positive (secondary: root-preserving, side-consistency not required) | 1,276,138 rewirings | **0 violations** |
| T1-negative | 33,590,682 candidate rewirings | **17,460,812 verdict changes** |
| ablation: shallow `S_a` | 50,362 exhaustive worlds | **caught on 24,984** |
| ablation: claim-count | 50,362 exhaustive worlds | **caught on 21,440** |
| ablation: shallow `S_a` | 100,000 randomized worlds | **caught on 18,994** |
| ablation: claim-count | 100,000 randomized worlds | **caught on 34,779** |

33,647,922 rewirings enumerated in total (`Σ_k count(k)·k!`), every one checked in
both implementations, which agree exactly.

Two incidental structural facts, both verified rather than assumed. L1-negative
fires on *every* side-inconsistent world, not merely some — because any
side-flip along a chain puts that chain's root into `S_{1−side(root)}`, where the
root-set never has it. And the exhaustive verdict census is exactly symmetric
(15,477 / 15,477 / 19,408 abstain), as the 0↔1 relabelling symmetry of the
enumeration requires.

### 5.1 The result worth the commission: T1's truth value is undefined

The registration says: *"under root-preserving, side-consistent rewiring the
verdict MUST NOT change. Violations MUST be 0."* Neither "rewiring" nor
"root-preserving" is defined, and "side-consistent" does not say whether it
constrains the rewiring alone or the original world too. Taking a rewiring to be
"same `k`, same sides, any valid parent vector", four readings remain admissible.
I tested all four (`checks/q3-boundary.mjs`):

| reading | "root-preserving" | original required side-consistent? | rewirings | violations |
|---|---|---|---|---|
| A (**mine, pre-declared**) | `root(c)` preserved ∀c | yes | 57,240 | **0** |
| B | only the *set* of root claims preserved | yes | 121,944 | **0** |
| C | `root(c)` preserved ∀c | no | 57,240 | **0** |
| D | only the *set* of root claims preserved | no | 200,024 | **47,224** |

**Reading D is a defensible parse of the registered sentence, and under it the
registration's "Violations MUST be 0" is false 47,224 times.** Smallest
counterexample, at `k = 3`:

```
original :  -|0 ; -|1 ; 0|1     side-inconsistent   verdict = 1
rewired  :  -|0 ; -|1 ; 1|1     side-consistent     verdict = abstain
```

Claims 0 and 1 are roots in both worlds and claim 2 is not, so the *set* of root
claims is preserved; sides are untouched; the rewired world is side-consistent.
Only `root(2)` moves, from 0 to 1 — which is precisely what reading A forbids and
reading D permits. `S_1` goes from `{0,1}` to `{1}`, and the verdict flips from 1
to abstain.

So the registration does not currently determine whether T1-positive holds. It is
one sentence away from doing so.

I record a correction against my own pre-declaration: `DECISIONS.md` §R23 asserted
that the weak reading of root-preservation would make T1-positive false. That is
wrong as stated — reading B holds with 0 violations, because side-consistency plus
Lemma 1 forces `S_a` to equal the root set, which the weak reading preserves. The
failure needs *both* halves of the loosening (weak root-preservation **and** an
unconstrained original), which is reading D. My prediction identified the right
term and the wrong boundary.

### 5.2 T1-positive is a corollary, not a test

Under readings A–C, T1-positive cannot fail — and not by luck. `S_a` is defined as
`{root(c) : side(c) = a}`, so it is a function of the multiset of `(root(c),
side(c))` pairs alone; a rewiring that preserves every `root(c)` and touches no
side leaves `S_0`, `S_1` and hence the verdict identical, by construction. That is
why the secondary run over 1,276,138 root-preserving rewirings — with
side-consistency not even required — also returns 0.

This is a definitional identity appearing under the heading **"Tests that can
fail"**. It cannot. Its 0 is not evidence about the schema; it is evidence that my
`S_a` matches the registered one, which the digests already established. The
genuine content in that section is T1-negative (17.5M verdict changes, so the
positive case is not vacuous), L1, and the two ablations — all of which do carry
information, and all of which passed.

---

## 6. Things I believe are wrong in `REGISTRATION-v0.2.md`

**W1 — §Tests: "rewiring" and "root-preserving" are undefined, and the omission
decides the theorem.** Severity: high; see §5.1. Suggested repair, which costs one
sentence: *"A rewiring of a world is a world with the same k and the same side
vector, differing only in parentIndex. It is root-preserving iff root(c) is
unchanged for every claim c. T1-positive ranges over side-consistent worlds and
their side-consistent root-preserving rewirings."* With that, readings B, C and D
are excluded and the registered expectation becomes true and checkable.

**W2 — §Tests: T1-positive is filed under "Tests that can fail" and cannot fail.**
Severity: medium; see §5.2. Either state it as a corollary of the definition of
`S_a` (honest, and still worth asserting), or strengthen it into something falsifiable
— e.g. require invariance under rewirings that preserve only the *root multiset*,
which is reading B and is a real theorem rather than an identity.

**W3 — §Generator: "The word cost of a world is therefore fully determined by its
own outcomes" is false as written.** Word cost depends on the *words*, not on the
world's outcomes: a rejected word costs a draw and leaves no trace in the world.
Two worlds with identical claims can cost different numbers of words. True in this
run only because no rejection occurred (W4). Repair: "...determined by its own
outcomes together with the number of rejected words".

**W4 — the rejection rule, which is D1's whole point, is never exercised by the
pinned artifact.** Severity: high, and this is the one I would fix first after W1.
Measured over the actual draw census (`checks/edge-cases.mjs`):

- 2,759,273 draws, **0 rejections observed**;
- expected rejections **2.97 × 10⁻³**; P(at least one) ≈ **0.30%**;
- for `n ∈ {1,2,4,8,16}`, `2³² mod n = 0`, so rejection is *impossible* by
  construction; for the rest, at most 16 of 2³² words are rejectable.

So an implementation that gets the rejection rule wrong — `w <= limit`,
re-drawing without consuming, Lemire's multiply-shift, or omitting rejection
entirely — **still reproduces both pinned digests**. The most carefully specified
clause in the repair is the one clause the experiment does not test. It survives
here only because the degenerate `n = 1` case (which the same paragraph fixes) *is*
exercised, 66,427 times. Repair: ship a fixture that forces the branch — a short
declared table of `(word sequence, n) → output` including a word ≥ `limit`, with
its own digest. It costs a few lines and converts an untested clause into a tested
one. Note that this is a *coverage* gap, not a correctness gap: the rule as
written is unambiguous, and I implemented it faithfully.

**W5 — §Tests: both ablations are named but not defined.** "a shallow-`S_a` and a
claim-count ablation MUST each be caught" fixes neither the construction nor what
"caught" means. My definitions and counts are in `DECISIONS.md` §R24 and §5 above;
another implementer would plausibly choose differently and report incomparable
numbers. Same for L1-negative's unstated population (§R22).

**W6 — §Schema: `id` is an unbound field.** It appears in the world schema, has no
generation rule in either phase, and does not enter the canonical form. Harmless
in effect, but it is a free variable in a registration whose stated purpose is to
leave nothing free.

**W7 — §Invalidation: "any `uniform_below` implemented with a float" is phrased as
a code-inspection condition.** A verifier holding only the artifact cannot check
it. As §4 shows, it is enforced by the digest anyway; better to say so.

Nothing else in the registration disagreed with what I measured. The count
identity, the declared total, the enumeration order, the canonical form, the draw
schedule, and the prefix-digest scheme are all correct as written, and §Why v0.2's
account of D1–D3 matches what I observed when I perturbed those decisions.

---

## 7. Method compliance, and what this run does *not* establish

Per `RESEARCH-METHOD.md`:

- Phases reached: `specification → fixture → exhaustive-small → randomized`. The
  variant sweep in §4 and the reading-boundary search in §5.1 are adversarial in
  character but were not a registered adversarial phase. Nothing beyond
  `randomized` is claimed, and later gates were not attempted.
- **Independent verification**: two implementations, two languages, two SHA-256
  code paths, agreeing on every reported field before the pinned file was opened.
  Both were written by the same author, so this bounds implementation error, not
  author error. The genuinely independent check is against the withheld v0.2
  reference, which the digest agreement supplies.
- **Claim discipline.** Replaying these bytes establishes cross-language
  reproducibility of a frozen synthetic model. It establishes nothing about
  lineage-bearing verdicts on real evidence, and no such claim is made here.
- **Evidence package**: `RUN-MANIFEST.json` — environment, toolchain versions,
  build command, UTC timestamps, and SHA-256 of every input, source file and
  output. No secrets or private data. The package is not a git repository, so no
  commit or worktree state exists to record; that is noted in the manifest rather
  than left blank.
- **Human intervention**: none during the run. The reading was frozen, the
  programs were written, they were run once each, and the comparison was made
  once. There was no second attempt at either digest.

---

## 8. Bottom line for the programme

v0.1's conclusion was that registering a draw schedule in prose is *necessary but
not sufficient* — it buys "one coin-flip away", not a stream. v0.2 replaced the
prose with a defined generator, primitive-level draws, decided boundaries and a
registered order.

**On this run, that was sufficient.** A reader with the registration, no reference,
no Python and no feedback reproduced both streams exactly, on the first attempt,
in two languages, after pre-declaring the reading. Of 19 perturbed readings tested,
all 19 miss, each with a distinct digest — so the sufficiency comes from
the added clauses, not from slack.

The remaining gap has moved, cleanly, from the stream to the theorems. v0.2's
digest-bearing text is now, as far as I can measure it, unambiguous. Its
test-bearing text is not: four choices were left to me, one of them decides
whether a registered "MUST be 0" is true (§5.1), another makes a registered test
unfalsifiable (§5.2), and the repair's central clause is never exercised by the
artifact meant to test it (§W4).

If there is a v0.3, D1–D3 do not need revisiting. The list is W1, W4, W2, W5.
