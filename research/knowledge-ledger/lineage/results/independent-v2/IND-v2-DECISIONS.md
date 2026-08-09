# Pre-declared reading — LIN-000 v0.2, independent reimplementation (BL-051)

**Frozen before any implementation was written, any stream was generated, and any
digest was compared.** Nothing below was revised after seeing a result. Revisions,
if any were forced, are recorded in `FINDING-BL051.md` as amendments with reasons,
never by editing this file.

- Implementer: independent agent, commissioned by RUN-20260808-3 via `BRIEF.md`.
- Date frozen: 2026-08-09.
- Inputs read, in order: `BRIEF.md`, `REGISTRATION-v0.2.md`, `PINNED-DIGESTS.json`,
  `RESEARCH-METHOD.md`. `MANIFEST.sha256` verified (`shasum -a 256 -c`) — all 4
  files OK.
- **The reference implementations were not read.** Nothing under
  `research/knowledge-ledger/lineage/` was opened, listed, or searched. No file
  outside this package was read.
- **No Python.** Primary implementation: Rust, with SHA-256 written by hand from
  FIPS 180-4 (no crate, no system library). Cross-check implementation: JavaScript
  on Node.js, written separately, using `node:crypto`. Two languages, two
  independent SHA-256 code paths.

What follows is the reading I commit to. Where the registration left a choice, I
state the choice, the alternatives I rejected, and why.

---

## Part 1 — Generator

### R1. Seed encoding — `seed_be`

**Chosen:** `seed_be = uint64_be(20260808)` = `00 00 00 00 01 35 27 C8`.

**Rejected:** ASCII `"20260808"` = `32 30 32 36 30 38 30 38`. This is a real trap,
not a straw man: the decimal representation of the seed is *exactly eight bytes*,
so "encoded as 8 bytes" alone does not separate the two. The word "big-endian"
does: a byte string has no endianness, so the phrase is only meaningful for an
integer encoding. Decided on that basis.

**Rejected:** little-endian; 4-byte encodings; the integer as a decimal string
zero-padded or otherwise.

### R2. Block index encoding

**Chosen:** `block(m) = SHA-256(seed_be || uint64_be(m))`, a 16-byte message,
`m` counting from 0. No separator, no length prefix, no domain tag.

### R3. Word extraction

**Chosen:** `w(i) = uint32_be(block(i // 8)[4*(i%8) .. 4*(i%8)+4])`. Eight words
per block, in byte order within the block. `w(0)` is the first four bytes of
`block(0)`.

### R4. `uniform_below(n)`

**Chosen, verbatim from the registration:**

    limit = 2**32 - (2**32 mod n)
    loop: take next word w; if w < limit return w mod n; else discard and repeat

- Rejected words **are consumed** — they advance the stream position.
- `uniform_below(1)`: `limit = 2**32`, no word can be rejected, **consumes exactly
  one word**, returns 0. No short-circuit. (Registration §`uniform_below`, D2.)
- All arithmetic in 64-bit unsigned; `2**32 mod n` is never approximated by
  `(2**32 - 1) mod n`.
- **No float appears anywhere in the sampler.** (Invalidation condition.)

### R5. Stream continuity

**Chosen:** one infinite stream for the whole randomized phase. Draws are consumed
strictly in order starting at `w(0)`; world *j*'s first draw begins at the first
word left unconsumed by world *j−1*. The stream is never reset, reseeded, or
re-aligned to a block or world boundary.

**Rejected:** per-world reseeding; per-world block alignment; skipping the
remainder of a block between worlds. Nothing in the text supports any of these,
and §Generator's "Draws are consumed strictly in order, starting at `w(0)`"
excludes them.

### R6. Scope of the generator

**Chosen:** the generator is consumed by the **randomized phase only**. The
exhaustive phase consumes zero words ("That phase contains no PRNG", D3). The two
phases do not share stream position because the exhaustive phase has none.

---

## Part 2 — Randomized phase

### R7. Per-world, per-claim draw schedule

**Chosen, in exactly this order, 100,000 worlds:**

```
k = 1 + uniform_below(20)                      # k in 1..20
for i = 0 .. k-1:
    if i == 0:
        is_root = true                          # NO draw consumed
    else:
        is_root = (uniform_below(10) < 3)       # 1 draw
    if is_root:
        parentIndex = null                      # NO draw consumed
        side = uniform_below(2)                 # 1 draw
    else:
        parentIndex = uniform_below(i)          # 1 draw (i == 1 -> uniform_below(1))
        keep = (uniform_below(10) < 9)          # 1 draw
        side = side[parentIndex] if keep else 1 - side[parentIndex]
```

Per-claim draw order is **root decision, then parent, then side** — the order the
registration lists them in.

### R8. Claim 0

**Chosen: no draw is consumed for claim 0's root decision.** Claim 0 is a root by
fiat; its only draw is `side = uniform_below(2)`. Claim 0 therefore costs exactly
one word (barring rejection). Decided by the registration, not by me — this was
v0.1's coin-flip (implementer's R3) and v0.2 states it.

### R9. `uniform_below(i)` at i == 1

**Chosen: one word is consumed and 0 is returned.** A non-root claim at index 1
has only claim 0 available as a parent, but the draw still happens. This follows
from R4 and is the specific divergence the registration warns about ("an
implementation that short-circuits it will diverge and should").

### R10. Probability idioms

**Chosen:** `is_root` iff `uniform_below(10) < 3`; `keep` iff `uniform_below(10) < 9`.
Strict `<`, as written. No float, no `≤`.

---

## Part 3 — Exhaustive phase

### R11. Search space and count — derived independently

Position `i` ranges over `(i+1)` parent choices (`null` plus the `i` earlier
claims) and 2 sides, independently across positions, so

    count(k) = (prod_{i=0..k-1} (i+1)) * 2^k = k! * 2^k

    k=1: 1!*2   =      2
    k=2: 2!*4   =      8
    k=3: 3!*8   =     48
    k=4: 4!*16  =    384
    k=5: 5!*32  =  3,840
    k=6: 6!*64  = 46,080
    total       = 50,362

**Derived before reading the registration's figure as authority; it agrees with
the declared 50,362.** A mismatch would have been reported, not adopted.

### R12. Enumeration order

**Chosen:**

1. **Across k:** ascending `k = 1,2,3,4,5,6`. All worlds of a given `k` are
   emitted contiguously before any world of `k+1`.
2. **Within k:** odometer over positions `0..k-1` with **position `k-1` varying
   fastest and position `0` slowest** — i.e. position 0 is the most significant
   digit, position `k-1` the least.
3. **Within position `i`** (that digit's value order, `2(i+1)` values):
   **parent-major**, parents in the order `null, 0, 1, …, i-1`; and for each
   parent, `side = 0` before `side = 1`.

   Digit order for position `i`:
   `(null,0), (null,1), (0,0), (0,1), (1,0), (1,1), …, (i-1,0), (i-1,1)`.

**Rejected:** side-major within a position (side as the outer key); `null` placed
last or after the numeric parents; position 0 varying fastest; descending `k`;
interleaving `k` values; grouping side-consistent worlds separately.

### R13. Both classes emitted

Side-consistent **and** side-inconsistent worlds are enumerated, in one interleaved
sequence, in the odometer order above. No filtering. (Registration §Exhaustive.)

### R14. Frozen concrete prediction — the opening of the exhaustive stream

Committed here so the reading is falsifiable independently of any digest.

`k = 1` (2 worlds):

```
-|0
-|1
```

`k = 2` (8 worlds), in order:

```
-|0;-|0
-|0;-|1
-|0;0|0
-|0;0|1
-|1;-|0
-|1;-|1
-|1;0|0
-|1;0|1
```

The first 10 lines of the exhaustive stream are the concatenation of those, in
that order.

---

## Part 4 — Canonical form and digests

### R15. Rendering

**Chosen:** claim → `P|S`, where `P` is the decimal `parentIndex` or the single
ASCII character `-` (0x2D) for a root, and `S` is the decimal side (`0` or `1`).
Claims joined with `;` (0x3B) in ascending claim index. Each world terminated by
one `\n` (0x0A). No trailing `;`, no leading separator, no separator between
worlds beyond each world's own `\n`, no final marker after the last world. ASCII.

**Rejected:** a `;` after the last claim; `\r\n`; a separator character between
worlds; omitting the terminator on the final world; rendering `parentIndex` as
anything but bare decimal.

### R16. Stream digest

SHA-256 over that byte concatenation, computed incrementally over the whole phase.

### R17. Prefix digests

**Chosen:** the prefix digest at *N* is SHA-256 of the concatenation of the
renderings of worlds `1..N` **inclusive of each world's terminating `\n`**, for
`N = 1000, 2000, 3000, …` — every completed multiple of 1,000 worlds. It is the
digest of a genuine prefix of the same byte stream, not a digest of a block or a
chained digest.

Consequences of this reading, pre-computed: the exhaustive phase yields
`floor(50362/1000) = 50` prefix digests and its final prefix (50,000 worlds) is
**not** the total; the randomized phase yields 100 prefix digests and its 100th
**is** the total.

*Disclosure:* `PINNED-DIGESTS.json` carries exactly 50 and 100 entries
respectively, and its last randomized prefix equals its randomized total. I
noticed this before running, and it corroborates R17. I used the **count and
position** of the published entries, never their values, to fix this reading. No
digest value informed any decision in this document.

### R18. Use of prefix digests

Prefix digests will be consulted **only after** both totals have been computed and
compared, and **only** to localise a divergence by binary search. No parameter,
reading, or line of code will be changed to move a prefix digest toward a target.
If any reading changes after a comparison, it is recorded as an amendment in the
finding with the reason, and the result is reported as a swept result, not a
pre-declared hit.

---

## Part 5 — Semantics under test

### R19. `root(c)`

Walk `parentIndex` until `null`; return that claim's index. Terminates because
`parentIndex(c) < index(c)` always.

### R20. Side-consistency

A world is side-consistent iff for every non-root claim `c`,
`side(c) == side(parent(c))`. A world with no edges is vacuously side-consistent.

### R21. `S_a` and verdict

`S_a = { root(c) : c ranges over ALL claims, side(c) = a }` — a **set** of root
indices, deduplicated, computed over all claims and deliberately not restricted to
root claims. Verdict: `1` if `|S_1| > |S_0|`; `0` if `|S_0| > |S_1|`; `abstain` if
equal (τ = 0).

### R22. L1

- **L1-positive:** for every side-consistent world and each `a ∈ {0,1}`,
  `S_a == { r : parentIndex(r) = null and side(r) = a }`. Violations MUST be 0.
- **L1-negative:** count side-inconsistent worlds where `S_a` differs from that
  set for some `a`. MUST be > 0.

Population for both: the full exhaustive set (50,362 worlds). Also reported over
the 100,000 randomized worlds as a secondary check.

### R23. Rewiring — **the registration does not define this; this is my definition**

A **rewiring** of world `W` is a world `W'` with the same `k` and the **same side
vector**, differing only in the parent vector, where `parentIndex'(i) ∈ {null} ∪
{0..i-1}` for each `i`. There are `k!` such rewirings of any world (the identity
included). Sides are never altered by a rewiring; only edges move.

- `W'` is **root-preserving** iff `root_{W'}(c) = root_W(c)` for **every** claim
  `c` — not merely "the set of root claims is unchanged". I record the weaker
  reading as rejected: under it T1-positive is false, and a theorem the
  registration asserts MUST hold would fail for a definitional reason rather than
  a substantive one.
- `W'` is a **side-consistent rewiring** iff `W'` is side-consistent.

- **T1-positive:** for every side-consistent `W` in the exhaustive set and every
  rewiring `W'` that is root-preserving and side-consistent,
  `verdict(W') == verdict(W)`. Violations MUST be 0. Rewirings checked reported.
- **T1-negative:** rewirings `W'` that break root-preservation or side-consistency
  **and** change the verdict MUST exist (> 0), counted over the same population.

Population: all 50,362 exhaustive worlds × all `k!` rewirings each =
2·1 + 8·2 + 48·6 + 384·24 + 3,840·120 + 46,080·720 = **33,647,922** rewirings,
enumerated exhaustively. No sampling.

**Pre-declared expectation, stated so it cannot be claimed as a discovery
afterwards:** under R21 and R23, `S_a` is a function of the multiset of
`(root(c), side(c))` pairs alone, so *any* root-preserving rewiring leaves `S_0`,
`S_1` and hence the verdict fixed — side-consistency is not even needed. I expect
T1-positive to hold **trivially**, and I will report it as a weak test rather than
as confirmation. The informative results here are T1-negative and the ablations.

### R24. Ablations — **also not defined in the registration; these are my definitions**

Both are "caught" iff they disagree with the correct verdict on at least one
world; counts reported over the exhaustive set and the randomized set.

- **Shallow-`S_a`:** `S_a^shallow = { c : parentIndex(c) = null and side(c) = a }`
  — count only claims that are themselves roots, never walking parent edges.
- **Claim-count:** verdict from `|{c : side(c) = 1}|` vs `|{c : side(c) = 0}|`
  over all claims, ignoring lineage entirely.

---

## Part 6 — Run discipline

### R25. Double computation (invalidation condition)

Each phase's stream digest is computed **twice within the same run**, by two
independent passes, and the two must agree. A disagreement invalidates the run and
would be reported as such.

### R26. Independent cross-implementation

Both phases are computed by two separately written programs in two languages
(Rust with a hand-written SHA-256; JavaScript on Node.js with `node:crypto`). They
must agree with each other on both totals and all 150 prefix digests before either
is compared with `PINNED-DIGESTS.json`. This tests my own arithmetic, not the
registration.

### R27. Invalidation conditions carried from the registration

Run is invalid if: exhaustive count ≠ 50,362; any expected-nonzero count observed
zero; any `uniform_below` implemented with a float; any phase whose regenerated
digest differs from its first computation in the same run.

### R28. Order of operations

Implement → self-test SHA-256 against FIPS 180-4 vectors and against `shasum` →
cross-check the two implementations against each other → compute both totals →
**then, and only then**, open `PINNED-DIGESTS.json` for comparison. Report the
outcome as it falls.

---

## Ambiguities I judge to be genuinely unresolved by the registration

Listed here, before the run, so the count is not adjusted afterwards. Full
treatment in `FINDING-BL051.md`.

1. **R23 — "rewiring" is undefined.** The registration asserts T1 over rewirings
   without saying what may move (edges? sides? k?), what "root-preserving" means,
   or over which population. Any implementer must invent this. Highest-severity
   gap remaining in v0.2.
2. **R24 — the two ablations are named, not defined.** "a shallow-`S_a` and a
   claim-count ablation" fixes neither construction nor the catch criterion.
3. **R22 — L1-negative's population is unstated** (exhaustive? randomized? both?).
4. **R1 — seed encoding is one word away from ambiguous.** The decimal seed is
   exactly 8 bytes; only "big-endian" rules out ASCII.
5. **`id` in the schema is never defined or used.** It appears in the world
   schema, has no generation rule in either phase, and does not enter the
   canonical form. Harmless, but it is an unbound field in a registration whose
   purpose is to leave nothing unbound.

Everything in Parts 1–4 — the entire path to the two digests — I judge to be
**fully determined** by v0.2, with R1, R5 and R15 the places I had to think
rather than read. That judgment is itself testable, and the test is whether the
digests hit.
