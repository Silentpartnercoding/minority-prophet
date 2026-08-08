# LIN-000 — independent reimplementation (BL-044): results

Implementation: Rust 1.96.1, zero dependencies, hand-written SHA-256 and
MT19937. No Python was used at any point — not to implement, not to validate.
The reference implementation under `research/knowledge-ledger/lineage/` was not
opened. `MANIFEST.sha256` verifies clean against the three shipped files.

---

## 1. Headline

**Both published digests reproduce — but neither reproduces from the
registration as written.** Each required resolving one clause that
`REGISTRATION.md` leaves under-determined, and in each case I had to pick that
clause post-hoc from an enumerated space of readings rather than derive it.

| Phase | Pre-declared reading (frozen in `DECISIONS.md` before comparing) | Confirmed reading |
|---|---|---|
| exhaustive | **MISS** `a71c64eb…` | **MATCH** `b56d1228b7c9765381d046069c2a25e60cb2a406baabeed018e859a445a8ccbe` |
| randomized | **MISS** `2870b954…` | **MATCH** `f200184fd3f4d3c6ada4046ef4e751862d5ff70ce4ea0f6b1b8688d7dbdee2ca` |

The measurement that matters for F11 is not the match, it is the size of the
space the match had to be found in:

- **exhaustive**: 96 enumeration orders tried → **96 distinct digests**, exactly
  1 correct. Every ordering degree of freedom is stream-visible.
- **randomized**: 72 draw-schedule readings tried → exactly 1 correct.

So the verdict on the F11 repair is **necessary but not sufficient**, and the
insufficiency is sharply localised. Registering the schedule in prose got me
from "no cross-language stream exists at all" (a bare seed) to "one coin-flip
away". It did not get me to a stream.

The two failures are of different kinds, and the second is the more damaging:

1. **The randomized miss is the F11 clause failing at exactly one point.** Every
   hard part worked. The easy-looking part did not.
2. **The exhaustive miss has nothing to do with F11.** That phase contains no
   PRNG. It missed because the registration never states the enumeration order
   of a phase whose pass condition is an order-sensitive digest.

---

## 2. Independence and what I did not look at

- I did **not** read the reference implementation or `results/`.
- I did **not** consult the public repository, `PROVENANCE-REQUIREMENTS.md`,
  `formal/THEOREM-LEDGER.json`, or the RUN-20260807-10 draft run report — the
  files the brief says carry twelve of the fourteen counters. **Every counter in
  §6 was computed by my implementation and recognised from nothing.** I cannot
  tell you which of my counters are among the leaked twelve, because I did not
  look at the twelve.
- The only figures I was given are `50,362`, `100,000`, seed `20260808`, and the
  two digests. Of these, `50,362` I derived independently from
  `count(k) = k!·2^k` = 2 + 8 + 48 + 384 + 3,840 + 46,080 before comparing; it
  **agrees**, and my enumerator emits exactly 50,362 worlds.

**Discipline note.** `DECISIONS.md` was written and frozen before either digest
was computed. It records the primary reading, the rejected alternatives, and —
relevantly — flags R3 (claim 0's root-decision draw) in advance as "the decision
I am least sure of… a genuine coin-flip", predicting that the two readings
"diverge inside world 0". They diverge at world index 0. I got that clause
wrong, and had said beforehand that I might.

One deviation to declare: the randomized sweep space (72 readings) was
enumerated in `DECISIONS.md` **before** comparison. The exhaustive sweep space
was **widened post-hoc** — my first sweep tried only the 8 orderings I had
pre-enumerated, all missed, and I then added the `parents-outer` / `sides-outer`
layouts and ascending/descending variants (96 total). That widening is post-hoc
and I flag it as such. Nothing in the world model, the tests, or the counters
was tuned at any point; only these two presentational/schedule choices were
searched.

---

## 3. Primitive validation, without CPython

Reproducing the stream means reimplementing CPython's generator's *observable
behaviour*. Validating that against a local CPython would have reintroduced
exactly the circularity the brief forbids, so I validated against published
constants and an unrelated language:

| Check | Result |
|---|---|
| SHA-256 `""`, `"abc"`, FIPS 448-bit message | pass |
| SHA-256 of a 3 MB file, fed in ragged chunks, vs system `shasum -a 256` | identical |
| SHA-256 of `REGISTRATION.md` vs shipped `MANIFEST.sha256` | identical |
| MT19937 `init_genrand(5489)`, first 10 words vs the canonical default-seed sequence | pass |
| `init_by_array` + `genrand_res53`, 5 doubles vs **Ruby 2.6** `Random.new` | identical |
| `init_genrand(20260808)`, 6 words vs **Ruby 2.6** `Random.new(20260808)` | identical |

A correction worth recording: my first self-test asserted the 4th word of the
`init_by_array({0x123,0x234,0x345,0x456})` reference stream as `4107686914`. My
implementation produced `4107218783` while matching words 1–3. Three-of-four
agreement is impossible from a seeding bug, so I cross-checked against Ruby —
which confirmed `4107218783`. The misremembered vector was mine; the generator
was correct. The self-test now pins the Ruby-cross-checked values.

**That Ruby check is itself an F11 finding.** Ruby and CPython both implement
MT19937, and they produce *completely different streams from the same integer
seed* — Ruby shortcuts single-limb seeds to `init_genrand`, CPython always uses
`init_by_array`. Seed `20260808` gives CPython `2750719949, 2316572890, …` and
Ruby `1942550805, 2629425383, …`. So even a schedule that said "MT19937 seeded
with 20260808" — strictly more specific than what LIN-000 registers — would
still not fix a stream across two languages that both implement MT19937.

---

## 4. What the registration under-determines

### 4.1 The randomized draw schedule

Registered text: *"k uniform in 1..20; each claim: root with probability 0.3,
else parent uniform among earlier claims; side uniform for roots, else parent's
side with probability 0.9. The draw schedule is this sentence, in order, per
claim."*

The sentence fixes the *semantics* of each draw and the *order* of the draws. It
does not fix their **realization**, and the digest depends entirely on the
realization. Five clauses are stream-ambiguous:

| # | Clause | Readings | My pre-declared choice | Correct |
|---|---|---|---|---|
| R2 | `k uniform in 1..20` | `1+_randbelow(20)` (1 word + rejections) vs `1+int(random()*20)` (2 words) | `_randbelow(20)` | ✅ |
| R3 | does claim 0 consume the "root with probability 0.3" draw? | draw-and-discard vs short-circuit | draw-and-discard | ❌ **short-circuit** |
| R4 | `parent uniform among earlier claims` | `_randbelow(i)` vs `int(random()*i)` vs special-casing `i==1` | `_randbelow(i)` | ✅ |
| R5 | `side uniform for roots` | `_randbelow(2)` (2 bits + rejection) vs `getrandbits(1)` (1 word) vs `random()<0.5` (2 words) | `_randbelow(2)` | ✅ |
| R6 | `parent's side with probability 0.9` | keep iff `u<0.9` vs flip iff `u<0.1` — same distribution, **different stream** | keep iff `u<0.9` | ✅ |

Four of five right; the whole miss is R3.

**R3 is a hole in the prose, not a detail I overlooked.** "root with probability
0.3, **else** parent uniform among earlier claims" is *undefined* for claim 0:
the else-branch ranges over the empty set. Claim 0 is forced to be a root either
way, so the clause has no observable consequence for the *world* — only for the
*stream*, via whether two 32-bit words are consumed. The registration's own
instruction, "the draw schedule is this sentence, in order, per claim", reads
most naturally as *draw for every claim* (claim 0 is a claim); the reference
short-circuits. Both are defensible; the prose cannot distinguish them.

**R5 deserves emphasis even though I got it right.** "Side uniform" sounds
maximally simple and has three CPython realizations consuming different numbers
of words. `_randbelow(2)` is the counter-intuitive one: `n.bit_length()` for
n=2 is **2**, so it draws two bits and rejects half of them. I chose it because
both `randint(0,1)` and `choice((0,1))` reduce to it — a majority-of-idioms
argument, not something the registration says.

### 4.2 Draws actually consumed per claim (brief item 4)

From instrumenting the generator itself (`out/trace.txt`, world 0, confirmed
reading, k=18):

```
world   0  k       : _randbelow(20) -> k=18   [2 x 32-bit word(s)]
      claim  0 root  : no draw (claim 0 forced root)          [0]
      claim  0 side  : _randbelow(2) -> side=0                [1]
      claim  1 root  : random()=0.797443 < 0.3 -> false       [2]
      claim  1 parent: _randbelow(1) -> parent=0              [4]
      claim  1 side  : random()=0.027121 < 0.9 -> keep side 0 [2]
      claim  2 root  : random()=0.242917 < 0.3 -> true        [2]
      claim  2 side  : _randbelow(2) -> side=1                [3]
      ...
      => (94 words total)
```

Per claim, in order:
- **claim 0**: no root draw; then `_randbelow(2)` for side.
- **claim i>0, root**: `random()` (2 words); then `_randbelow(2)` for side.
- **claim i>0, non-root**: `random()` (2 words); then `_randbelow(i)` for the
  parent; then `random()` (2 words) for the 0.9 side test.

Note `_randbelow(1) -> parent=0` consuming **4 words** for a foregone
conclusion — it draws 1 bit and rejects every 1 until it sees a 0. An
implementer who reasonably writes `if i == 1: parent = 0` desynchronises the
entire remaining stream. Word counts for `_randbelow(2)` in this one world are
1, 3, 4, 2, … — rejection makes consumption data-dependent, so there is no
fixed "draws per claim" number to register even if one wanted to.

### 4.3 The exhaustive enumeration order

The registration defines *which* worlds are enumerated and never defines their
**order**. 96 orderings → 96 distinct digests. The correct one is:

> **two nested odometers — all parent tuples outer, all 2^k side assignments
> inner**; null before earlier indices; indices ascending; sides 0 then 1; last
> position varying fastest in both odometers.

My pre-declared reading was a *single interleaved* odometer whose per-position
digit ranges over `(parent, side)` pairs — i.e. `itertools.product` over
per-position option lists. Both are natural; the registration speaks to neither.
First divergence at **world index 4**: mine `-|0;0|0`, reference `-|1;-|0`.

Also: the canonical stream form (`;` join, `parentIndex|side`, `-` for roots,
`\n` terminator) appears **only in `BRIEF.md`**, never in `REGISTRATION.md`.
`BRIEF.md` states "`REGISTRATION.md` is the whole specification"; it is not — it
cannot produce either digest on its own.

### 4.4 Localisation (brief item 1)

The brief asks which world index first diverges. **A digest cannot answer that
against the reference** — a SHA-256 over the whole stream is exactly the
construction that destroys positional information, which is what makes it a good
pass condition and a useless diagnostic. Withholding the reference stream while
asking for byte-level cause localisation is not satisfiable as posed. What I can
localise is my pre-declared reading against the confirmed one:

- randomized: **world index 0**, at claim 0's side draw, and everything after.
- exhaustive: **world index 4** (first k=2 world where the two orders disagree).

---

## 5. Theorem 1 and Lemma 1 (brief item 3)

**Neither failed anywhere. No counterexample exists in this model.**

| | exhaustive | randomized |
|---|---|---|
| L1-positive worlds checked | 5,912 | 54,548 |
| **L1-positive violations** | **0** | **0** |
| T1-positive rewirings checked | 23,952 | 975,782 |
| **T1-positive violations** | **0** | **0** |

Both results are non-vacuous here in the way the paper's shadow-tested schema
made impossible: 5,786 of the 5,912 side-consistent exhaustive worlds contain at
least one non-root claim, so `root(c)` genuinely collapses chains, and 5,512
worlds admit at least one root-preserving side-consistent rewiring.

I also checked the registration's stated composition argument rather than
accepting it. It holds: rewiring never changes any claim's side, so if worlds A
and B are both side-consistent with the same root set, changing one claim's
parent at a time from A's to B's yields only valid intermediates (acyclicity is
automatic since parents are always earlier; side-consistency holds at each step
because `side(c) = side(B-parent(c))` already). The single-step scope is
therefore genuinely complete for arbitrary root-preserving side-consistent
rewirings.

---

## 6. Counters (brief item 2)

**All independently derived; none recognised.** See §2.

### Exhaustive phase — order-independent

These depend only on the world *set*, so they are identical under all 96
orderings; I verified they are byte-identical between the pre-declared and
confirmed runs.

| Counter | Value |
|---|---|
| worlds enumerated | **50,362** (= derived `k!·2^k`) |
| side-consistent | 5,912 |
| side-inconsistent | 44,450 |
| verdict 1 / 0 / abstain | 15,477 / 15,477 / 19,408 |
| L1-positive checked / **violations** | 5,912 / **0** |
| L1-negative worlds where `S_a` ≠ a-asserting roots | 44,450 |
| L1-negative scope-note (one root in both `S₀` and `S₁`) | 44,450 |
| T1-positive rewirings / base worlds / **violations** | 23,952 / 5,512 / **0** |
| T1-viol(i) orphan: rewirings / `S_a` changed / **verdict changed** | 15,890 / 15,890 / **5,244** |
| T1-viol(i) attach-root: rewirings / `S_a` changed / **verdict changed** | 15,890 / 15,890 / **5,244** |
| T1-viol(ii) cross-side: rewirings / `S_a` changed / **verdict changed** | 11,976 / 11,976 / **7,272** |
| ablation LB-shallow caught by T1-positive | 13,152 |
| ablation LB-shallow caught by L1-positive | 2,904 |
| ablation LB-claimcount caught by L1-positive | 5,786 |
| side-consistent worlds containing a non-root claim | 5,786 |

Three internal consistency checks, each provable rather than fitted, all pass:

- verdict 1 and verdict 0 are **exactly equal** (15,477 each) — the world set is
  closed under global side-swap, which negates the verdict.
- LB-claimcount's catch count (5,786) is **exactly** the number of
  side-consistent worlds with a non-root claim — precisely where dropping root
  collapse changes `S_a`.
- orphan and attach-root counts are **exactly equal** in both rewirings and
  verdict changes — the two operations are mutually inverse bijections on
  (world, claim) pairs.

### Randomized phase — confirmed reading, seed 20260808, 100,000 worlds

| Counter | Value |
|---|---|
| side-consistent / side-inconsistent | 54,548 / 45,452 |
| verdict 1 / 0 / abstain | 39,311 / 39,655 / 21,034 |
| L1-positive checked / **violations** | 54,548 / **0** |
| L1-negative `S_a` ≠ roots / scope-note | 45,452 / 45,452 |
| T1-positive rewirings / base worlds / **violations** | 975,782 / 41,895 / **0** |
| T1-viol(i) orphan: rewirings / **verdict changed** | 265,808 / **76,876** |
| T1-viol(i) attach-root: rewirings / **verdict changed** | 392,061 / **114,018** |
| T1-viol(ii) cross-side: rewirings / **verdict changed** | 403,764 / **164,456** |
| ablation LB-shallow caught by T1-positive / L1-positive | 558,414 / 34,651 |
| ablation LB-claimcount caught by L1-positive | 47,460 |
| k histogram | uniform, 4,813–5,089 per value |

### Pinned minimal two-claim L1-negative witness

`-|0;0|1` — claim 0 a root asserting 0, claim 1 its child asserting 1.
Side-inconsistent. `S₀ = {0}`, `S₁ = {0}`, roots asserting 1 = `{}`. So
`S₁ ≠ roots(1)`, and root 0 appears in **both** `S₀` and `S₁` — the paper's
scope-note phenomenon, at minimum size. Verdict: abstain.

### Ablations — both caught, checker is not vacuous

- **LB-shallow** caught by T1-positive: 13,152 exhaustive rewirings (required).
  It is *also* caught by L1-positive on 2,904 worlds — those containing a chain
  of length ≥ 2, where "one step up" stops short of the head.
- **LB-claimcount** caught by L1-positive: 5,786 exhaustive worlds (required).

### Invalidation conditions — none triggered

Count = 50,362 ✓ · stream regenerates identically ✓ · every expected-nonzero
counter is nonzero ✓ · both ablations caught ✓ · no L1-positive or T1-positive
violation ✓.

---

## 7. What I believe is wrong in `REGISTRATION.md` (brief item 5)

1. **The exhaustive enumeration order is never specified**, yet the pass
   condition is an order-sensitive digest. 96 plausible orders, 96 distinct
   digests. This defect involves no PRNG and would survive any F11 repair aimed
   at generators.
2. **The canonical stream form is not in the registration at all** — only in
   `BRIEF.md`. The registration cannot produce its own pass condition.
3. **The draw schedule is undefined for claim 0** (§4.1, R3). This is the clause
   that cost me the randomized digest.
4. **"`random.Random`" silently delegates four unnamed primitives to CPython**:
   integer-seed → 32-bit limb array → `init_by_array`; the 53-bit float built
   from two words; `getrandbits`; and `_randbelow`'s `bit_length`-plus-rejection.
   None is named in the registration. The F11 lesson line — "the schedule is
   registered, not just the seed" — is half-executed: the schedule of
   *decisions* is registered, the schedule of *draws* is not. I only reproduced
   the stream because I already knew CPython's internals; an implementer without
   that knowledge could not have derived them from this document.
5. **The invalidation clause "seed failing to reproduce an identical stream
   (regenerate-and-compare)" cannot detect the failure it exists for.**
   Regenerate-and-compare is a within-implementation determinism check. It
   passes trivially in a world where cross-implementation reproduction is
   impossible — which is precisely the F11 condition.
6. **L1-negative's "expected > 0" is unfalsifiable given a correct enumerator.**
   Every side-inconsistent world necessarily exhibits both phenomena: some edge
   joins claims of different sides, both endpoints share a root `r`, so `r ∈ S₀ ∩ S₁`,
   and `r` is in the `S_a` of the side it does not itself assert. Hence both
   counters are *identically* the side-inconsistent world count (44,450 and
   45,452 — note they are equal to it and to each other). The test measures the
   enumerator, not the checker. Replace ">0" with the predicted equality.
7. **LB-shallow is under-claimed**: stated as "MUST be caught by T1-positive",
   it is also caught by L1-positive on 2,904 worlds. Harmless, but the ablation
   is stronger than registered.
8. **The two T1-violation families don't say whether the other premise is held
   fixed.** I held it fixed — attach-root uses a same-side parent, so only the
   root set breaks — to isolate each premise. Different choices give different
   counts, so these counters are not comparable across implementations without
   the clarification.
9. Cosmetic: "position i has (i+1) parent choices" is 1-indexed while
   `parentIndex` is 0-indexed throughout the schema.

The composition argument in T1-positive (§5) is **sound**; I checked it rather
than assuming it.

---

## 8. Recommendation for the F11 repair

Registering the schedule in prose is a real improvement over a frozen seed and
should be kept — but on this evidence it is not sufficient, and the gap is not
closable by writing the same kind of sentence more carefully. Three changes:

1. **Name a language-neutral generator and its exact derivation.** Not
   "`random.Random`", and not even "MT19937 seeded with 20260808" — the Ruby
   result in §3 shows two conforming MT19937s diverge on that seed. Specify a
   counter-based construction the registration can state in full (e.g. draw *j*
   is `SHA-256(seed_bytes || j)` truncated), so the generator is defined by the
   document rather than referenced from it.
2. **Register draws as primitives, not as distributions.** "Uniform in 1..20"
   has multiple stream-distinct realizations; "consume one 32-bit word, reject
   and redraw while ≥ 20·⌊2³²/20⌋, return *w* mod 20" has one. Every place the
   schedule says "uniform" or "with probability p" needs the acceptance rule and
   the word count spelled out, including the degenerate cases (`_randbelow(1)`
   is not a no-op).
3. **Specify the boundary cases and the orders.** Claim 0's draw explicitly; the
   enumeration order of every deterministic phase; and the canonical stream form
   inside the registration rather than the covering brief.

A cheap structural addition: publish **prefix digests** (say every 1,000 worlds)
alongside the total. It costs nothing, leaks no more than the total already
does, and converts an unlocalisable miss into a binary search — which is what
the brief asks for in item 1 and what a bare digest cannot give.

---

## 9. Artifacts

```
src/sha256.rs  src/mt.rs  src/world.rs  src/main.rs   implementation
DECISIONS.md                                          readings, frozen pre-comparison
out/confirmed.txt   full run under the confirmed readings (both digests MATCH)
out/primary.txt     full run under the pre-declared readings (both MISS)
out/sweep.txt       96 orderings + 72 schedule readings, with divergence localisation
out/trace.txt       per-draw trace, first 2 worlds, both readings
out/exhaustive-sample.txt  out/randomized-sample.txt   first 40 worlds of each stream
```

Build and reproduce:

```
rustc -O -o out/lin000 src/main.rs
./out/lin000 selftest    # primitive validation
./out/lin000 confirmed   # both digests MATCH
./out/lin000 run         # pre-declared readings; both MISS
./out/lin000 sweep       # the ambiguity measurement
./out/lin000 trace       # draw schedule as executed
```
